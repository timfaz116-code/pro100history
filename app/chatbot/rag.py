import os
import math
import sqlite3
import struct
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

from openai import OpenAI
from app.chatbot.prompts import SYSTEM_PROMPT, RELEVANCE_CHECK_PROMPT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'storage', 'index.db')
EMBEDDING_DIM = 1536


def get_llm_client():
    api_key = os.environ.get('OPENAI_API_KEY', '')
    base_url = os.environ.get('OPENAI_BASE_URL', None)
    kwargs = {'api_key': api_key}
    if base_url:
        kwargs['base_url'] = base_url
    return OpenAI(**kwargs)


def get_embedding_model():
    return os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')


def get_llm_model():
    return os.environ.get('LLM_MODEL', 'gpt-4o-mini')


def blob_to_embedding(blob):
    n = len(blob) // 4
    return list(struct.unpack(f'<{n}f', blob))


def load_index():
    if not os.path.exists(DB_PATH):
        return None, None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT id, text, page FROM chunks ORDER BY id')
    chunks = [{'text': row[1], 'page': row[2]} for row in cursor.fetchall()]
    cursor = conn.execute('SELECT id, vec FROM embeddings ORDER BY id')
    embeddings = [blob_to_embedding(row[1]) for row in cursor.fetchall()]
    conn.close()
    return chunks, embeddings


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)


def embed_text(text):
    llm = get_llm_client()
    response = llm.embeddings.create(
        model=get_embedding_model(),
        input=text,
    )
    return response.data[0].embedding


def search_chunks(query, top_k=5):
    chunks, embeddings = load_index()
    if not chunks:
        return [], [], []

    query_emb = embed_text(query)
    similarities = []
    for i, stored_emb in enumerate(embeddings):
        sim = cosine_similarity(query_emb, stored_emb)
        similarities.append((sim, i))

    similarities.sort(key=lambda x: x[0], reverse=True)
    top = similarities[:top_k]

    documents = []
    metadatas = []
    distances = []
    for sim, idx in top:
        documents.append(chunks[idx]['text'])
        metadatas.append({'page': str(chunks[idx]['page']) if chunks[idx]['page'] else ''})
        distances.append(1 - sim)

    return documents, metadatas, distances


def relevance_check(query, chunks):
    if not chunks or not any(c.strip() for c in chunks):
        return False
    combined = '\n\n'.join(chunks[:3])
    prompt = f"""Фрагменты учебника:
{combined}

Вопрос ученика: {query}

{RELEVANCE_CHECK_PROMPT}"""
    try:
        llm = get_llm_client()
        response = llm.chat.completions.create(
            model=get_llm_model(),
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0,
            max_tokens=10,
        )
        answer = response.choices[0].message.content.strip().lower()
        return 'да' in answer
    except Exception:
        return True


def get_answer(question, history=None):
    documents, metadatas, distances = search_chunks(question, top_k=5)

    has_relevant = bool(documents) and relevance_check(question, documents)

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    if history:
        for entry in history:
            role = 'user' if entry.get('role') == 'user' else 'assistant'
            messages.append({'role': role, 'content': entry.get('content', '')})

    if has_relevant:
        context_parts = []
        for i, doc in enumerate(documents):
            page = metadatas[i].get('page', '') if metadatas and i < len(metadatas) else ''
            page_str = f' (стр. {page})' if page else ''
            context_parts.append(f'Фрагмент {i + 1}{page_str}:\n{doc}')

        context = '\n\n'.join(context_parts)
        messages.append({'role': 'user', 'content': f'Контекст из учебника:\n\n{context}\n\nВопрос ученика: {question}'})
    else:
        messages.append({'role': 'user', 'content': f'Вопрос ученика: {question}'})

    llm = get_llm_client()
    response = llm.chat.completions.create(
        model=get_llm_model(),
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )
    answer = response.choices[0].message.content

    sources = []
    base_pdf_url = 'https://raw.githubusercontent.com/timfaz116-code/pro100history/main/knowledge/history_textbook.pdf'
    for i, doc in enumerate(documents):
        page = metadatas[i].get('page', '') if metadatas and i < len(metadatas) else ''
        sources.append({
            'fragment': doc[:200] + ('...' if len(doc) > 200 else ''),
            'page': page if page else None,
            'page_url': f'{base_pdf_url}#page={page}' if page else None,
        })

    return {'answer': answer, 'sources': sources}
