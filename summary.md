# Project Summary

## Goal
Make a history textbook chatbot (RAG-based) with persistent conversation context across sessions, hosted on PythonAnywhere.

## Constraints & Preferences
- Bot answers only from textbook content (RAG via OpenRouter: deepseek/deepseek-chat, text-embedding-3-small)
- Conversation history saved in DB (survives page refresh)
- Last 8 messages in LLM context (stay within OpenRouter free tier ~7471 tokens)
- Sources clickable with PDF page links via `raw.githubusercontent.com` URL with `#page=N` (no offset)
- Flask + SQLAlchemy (SQLite), hosted on PythonAnywhere
- Tilda-exported frontend needs to work on mobile (iPhone 13 Safari)

## Done
- ChatMessage model (id, conversation_id, role, content, created_at) for persistent history
- `ensure_table()` in routes.py lazy-creates chat_messages table on first request (avoids WSGI import bug)
- Client generates conversation_id (localStorage), sends with every request, restores history via GET /api/chat/history
- Server loads last 8 history entries into LLM context; RAG fallback still answers from history if no textbook match
- page_url field on sources linked to raw PDF with #page=N anchor
- Removed 25 MTProxy-related files from repo
- Mobile scaling: whole Tilda page (`#allrecords`) scales via CSS `transform: scale()` proportionally on mobile; chatbot (fixed-position) stays correctly sized
- Chatbot responsive styles for 640px and 380px breakpoints (full-width, larger touch targets, 16px input font to prevent iOS zoom)

## Key Decisions
- `db.create_all()` moved to lazy `ensure_table()` — WSGI raised `TypeError: 'module' object is not callable` when import was inside `create_app()`
- `raw.githubusercontent.com`, not `github.com/blob` — blob viewer ignores `#page=N`
- PDF page numbers match textbook page numbers exactly (no offset)
- Page-level scale approach (not element restructuring) for mobile — Tilda's absolute-positioned elements can't be reliably restacked with CSS

## Important Context
- OpenRouter free tier: ~7471 prompt tokens; full history causes Error 402
- Tilda export: T396 blocks with inline absolute positioning set by JS — CSS-only overrides unreliable
- chat_messages table created lazily on first API call
- Commits: 1c93c65 (proportional scale), 9b32ca4 (original responsive fixes), 9121f30 (MTProxy removal), plus earlier history/PDF/RAG commits

## Relevant Files
- `app/chatbot/routes.py` — POST /api/chat, GET /api/chat/history, DB persistence, lazy table creation
- `app/chatbot/rag.py` — get_answer() with history limiting (8 messages), relevance check, PDF source links
- `app/chatbot/prompts.py` — SYSTEM_PROMPT with history usage instruction
- `app/models.py` — ChatMessage model
- `page143896526.html` — Full frontend (chatbot JS, responsive CSS, scale script, PDF links)
- `app/__init__.py` — Flask app factory (no db.create_all())
- `app/extensions.py` — db, login_manager init
- `config.py` — SQLite path (ege_history.db)
- `knowledge/history_textbook.pdf` — Source textbook
- `summary.md` — This file
