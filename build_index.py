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
import warnings
import re

warnings.filterwarnings('ignore', category=DeprecationWarning)

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge')
CHROMA_DIR = os.path.join(BASE_DIR, 'storage', 'chroma')

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def get_text_from_pdf(path):
    try:
        import pdfplumber
    except ImportError:
        print("Установите pdfplumber: pip install pdfplumber")
        raise

    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({'page': i + 1, 'text': text.strip()})
    return pages


def get_text_from_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [{'page': None, 'text': text}]


def chunk_text(pages):
    chunks = []
    for page in pages:
        text = page['text']
        page_num = page['page']
        paragraphs = re.split(r'\n\s*\n', text)

        current_chunk = ''
        for para in paragraphs:
            para = para.strip()
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

    merged = []
    for chunk in chunks:
        if merged and merged[-1]['text'].endswith('...'):
            merged[-1]['text'] += ' ' + chunk['text']
            continue
        merged.append(chunk)

    return merged


def get_embedding_model():
    return os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')


def embed_text(text, client):
    response = client.embeddings.create(
        model=get_embedding_model(),
        input=text,
    )
    return response.data[0].embedding


def main():
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        print("ОШИБКА: Не найден OPENAI_API_KEY.")
        print("Создайте файл .env в корне проекта и добавьте:")
        print("  OPENAI_API_KEY=ваш_ключ")
        print("\nПолучить ключ: https://platform.openai.com/api-keys")
        print()
        print("Если OpenAI недоступен в вашем регионе, используйте OpenRouter или DeepSeek:")
        print("  OPENAI_BASE_URL=https://openrouter.ai/api/v1")
        print("  OPENAI_API_KEY=sk-or-...")
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

    print("Подключение к ChromaDB...")
    db = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        db.delete_collection('history_textbook')
    except Exception:
        pass

    collection = db.create_collection(name='history_textbook')

    print("Создание эмбеддингов и загрузка в индекс...")
    base_url = os.environ.get('OPENAI_BASE_URL', None)
    client_kwargs = {'api_key': api_key}
    if base_url:
        client_kwargs['base_url'] = base_url
    client = OpenAI(**client_kwargs)

    ids = []
    texts = []
    metadatas = []
    embeddings = []

    for i, chunk in enumerate(chunks):
        ids.append(f'chunk_{i}')
        texts.append(chunk['text'])
        metadatas.append({
            'page': str(chunk['page']) if chunk['page'] else '',
            'chunk_id': i,
        })

    BATCH_SIZE = 20
    for start in range(0, len(texts), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(texts))
        batch_texts = texts[start:end]
        batch_ids = ids[start:end]
        batch_metas = metadatas[start:end]

        print(f"  Обработка фрагментов {start + 1}–{end} из {len(texts)}...")
        response = client.embeddings.create(
            model='text-embedding-3-small',
            input=batch_texts,
        )
        batch_embeddings = [r.embedding for r in response.data]

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_metas,
            embeddings=batch_embeddings,
        )

    print()
    print("Готово! Индекс создан.")
    print(f"  Файл: {os.path.basename(source_path)}")
    print(f"  Фрагментов: {len(chunks)}")
    print(f"  Хранилище: {CHROMA_DIR}")
    print()
    print("Теперь можно запустить сайт и задавать вопросы чат-боту.")


if __name__ == '__main__':
    main()
