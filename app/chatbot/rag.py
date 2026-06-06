import os
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from app.chatbot.prompts import SYSTEM_PROMPT, RELEVANCE_CHECK_PROMPT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DIR = os.path.join(BASE_DIR, 'storage', 'chroma')

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


def get_chroma_collection():
    db = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return db.get_or_create_collection(name='history_textbook')


def embed_text(text):
    llm = get_llm_client()
    response = llm.embeddings.create(
        model=get_embedding_model(),
        input=text,
    )
    return response.data[0].embedding


def search_chunks(query, top_k=5):
    collection = get_chroma_collection()
    query_embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances'],
    )
    return results


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


def get_answer(question):
    search_results = search_chunks(question, top_k=5)

    documents = search_results.get('documents', [[]])[0]
    metadatas = search_results.get('metadatas', [[]])[0]
    distances = search_results.get('distances', [[]])[0]

    if not documents:
        return {
            'answer': 'В загруженном учебнике нет достаточной информации для ответа на этот вопрос.',
            'sources': [],
        }

    has_relevant = relevance_check(question, documents)
    if not has_relevant:
        return {
            'answer': 'В загруженном учебнике нет достаточной информации для ответа на этот вопрос.',
            'sources': [],
        }

    context_parts = []
    for i, doc in enumerate(documents):
        page = metadatas[i].get('page', '') if metadatas and i < len(metadatas) else ''
        page_str = f' (стр. {page})' if page else ''
        context_parts.append(f'Фрагмент {i + 1}{page_str}:\n{doc}')

    context = '\n\n'.join(context_parts)

    llm = get_llm_client()
    response = llm.chat.completions.create(
        model=get_llm_model(),
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f'Контекст из учебника:\n\n{context}\n\nВопрос ученика: {question}'},
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    answer = response.choices[0].message.content

    sources = []
    for i, doc in enumerate(documents):
        page = metadatas[i].get('page', '') if metadatas and i < len(metadatas) else ''
        sources.append({
            'fragment': doc[:200] + ('...' if len(doc) > 200 else ''),
            'page': page if page else None,
        })

    return {'answer': answer, 'sources': sources}
