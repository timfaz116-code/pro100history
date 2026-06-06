"""
Индексация учебника для RAG-бота.

Использование:
    python build_index.py

Перед запуском:
    1. Положите учебник в папку knowledge/ (PDF или TXT)
    2. Создайте файл .env с OPENAI_API_KEY=your_key
    3. Установите зависимости: pip install -r requirements.txt

Поддерживаемые форматы:
    - PDF (только текстовый, не скан!)
    - TXT (UTF-8)
"""

import os
import glob
import json
import math
import re
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge')
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
INDEX_PATH = os.path.join(STORAGE_DIR, 'index.json')

CHUNK_SIZE = 800


def get_text_from_pdf(path):
    try:
        import pdfplumber
    except ImportError:
        print("Установите pdfplumber: pip install pdfplumber")
        raise

    pages = []
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            if (i + 1) % 50 == 0 or i == 0 or i == total - 1:
                print(f"  Страница {i + 1} из {total}...")
            text = page.extract_text()
            if text and text.strip():
                text = clean_text(text.strip())
                pages.append({'page': i + 1, 'text': text})
    return pages


def get_text_from_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [{'page': None, 'text': clean_text(text)}]


def chunk_text(pages):
    chunks = []
    for page in pages:
        text = page['text']
        page_num = page['page']
        paragraphs = re.split(r'\n\s*\n', text)

        current_chunk = ''
        for para in paragraphs:
            para = clean_text(para.strip())
            if not para:
                continue
            if len(current_chunk) + len(para) <= CHUNK_SIZE:
                current_chunk = (current_chunk + '\n\n' + para).strip()
            else:
                if current_chunk:
                    chunks.append({'text': current_chunk, 'page': page_num})
                current_chunk = para
        if current_chunk:
            chunks.append({'text': current_chunk, 'page': page_num})
    return chunks


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)


def clean_text(text):
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)


def main():
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        print("ОШИБКА: Не найден OPENAI_API_KEY.")
        print("Создайте файл .env в корне проекта и добавьте:")
        print("  OPENAI_API_KEY=ваш_ключ")
        print()
        print("Для OpenRouter:")
        print("  OPENAI_API_KEY=sk-or-...")
        print("  OPENAI_BASE_URL=https://openrouter.ai/api/v1")
        print("  EMBEDDING_MODEL=openai/text-embedding-3-small")
        return

    pdf_files = glob.glob(os.path.join(KNOWLEDGE_DIR, '*.pdf'))
    txt_files = glob.glob(os.path.join(KNOWLEDGE_DIR, '*.txt'))

    if not pdf_files and not txt_files:
        print(f"В папке {KNOWLEDGE_DIR} не найдено PDF или TXT файлов.")
        print("Положите туда учебник и запустите скрипт снова.")
        return

    source_path = None
    use_pdf = False
    if pdf_files:
        source_path = pdf_files[0]
        use_pdf = True
        print(f"Найден PDF-файл: {os.path.basename(source_path)}")
    else:
        source_path = txt_files[0]
        print(f"Найден TXT-файл: {os.path.basename(source_path)}")

    print("Извлечение текста...")
    if use_pdf:
        pages = get_text_from_pdf(source_path)
    else:
        pages = get_text_from_txt(source_path)

    if not pages:
        print("Не удалось извлечь текст из файла.")
        print("Если это PDF-скан, используйте PDF с текстовым слоем (OCR).")
        return

    print(f"Извлечено {len(pages)} страниц/блоков текста.")

    print("Разбивка на фрагменты...")
    chunks = chunk_text(pages)
    print(f"Получено {len(chunks)} фрагментов.")

    print("Создание эмбеддингов...")
    base_url = os.environ.get('OPENAI_BASE_URL', None)
    embedding_model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')

    client_kwargs = {'api_key': api_key}
    if base_url:
        client_kwargs['base_url'] = base_url
    client = OpenAI(**client_kwargs)

    index_data = {
        'chunks': [],
        'embeddings': [],
    }

    BATCH_SIZE = 20
    for start in range(0, len(chunks), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(chunks))
        batch = chunks[start:end]
        batch_texts = [c['text'] for c in batch]

        print(f"  Фрагменты {start + 1}–{end} из {len(chunks)}...")
        response = client.embeddings.create(
            model=embedding_model,
            input=batch_texts,
        )

        for i, chunk in enumerate(batch):
            index_data['chunks'].append(chunk)
            index_data['embeddings'].append(response.data[i].embedding)

    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False)

    print()
    print("Готово! Индекс создан.")
    print(f"  Файл: {os.path.basename(source_path)}")
    print(f"  Фрагментов: {len(chunks)}")
    print(f"  Индекс: {INDEX_PATH}")
    print()
    print("Теперь можно запустить сайт и задавать вопросы чат-боту.")


if __name__ == '__main__':
    main()
