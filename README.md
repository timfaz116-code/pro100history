# HistoryEge — Подготовка к ЕГЭ по истории

Веб-приложение для подготовки к ЕГЭ по истории: регистрация, личный кабинет, расписание, обучение по темам, тесты и контроль прогресса.

## Технологии

- Python + Flask
- SQLite + SQLAlchemy
- Jinja2-шаблоны
- HTML, CSS, JavaScript (чистые, без фреймворков)

## Установка и запуск

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
```

Активируйте:

- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Заполните базу тестовыми данными

```bash
python seed.py
```

Эта команда создаст базу данных `ege_history.db` и заполнит её:
- Учётки пользователей: `student@example.com` / `123456`
- 13 разделов истории
- Набор заданий по темам
- Расписание занятий (6 занятий)

### 4. Запустите приложение

```bash
python run.py
```

Приложение будет доступно по адресу: http://127.0.0.1:5000

### 5. Пересоздание базы

Если нужно сбросить данные, удалите файл `ege_history.db` и запустите `python seed.py` заново.

## Структура проекта

```
app/
  __init__.py          — фабрика приложения
  models.py            — модели SQLAlchemy
  extensions.py        — db, login_manager
  auth/
    routes.py, forms.py
  main/
    routes.py
  dashboard/
    routes.py
  learning/
    routes.py
static/
  css/style.css
  js/main.js
templates/
  base.html
  index.html
  auth/login.html, register.html
  dashboard/dashboard.html, schedule.html, progress.html
  learning/topics.html, tasks.html, test_result.html
run.py
config.py
seed.py
requirements.txt
README.md
```

## Чат-бот «ИИисторик» (RAG по учебнику)

На сайте есть диалоговый помощник, который отвечает на вопросы по истории **только на основе загруженного учебника**.

### Как это работает

1. Вы кладёте учебник (PDF или TXT) в папку `knowledge/`
2. Запускаете `python build_index.py` — скрипт разобьёт текст на фрагменты и создаст векторный индекс
3. При вопросе ученика система находит релевантные фрагменты в индексе и передаёт их в LLM (OpenAI)
4. Бот отвечает только по этим фрагментам. Если информации нет — честно сообщает об этом

### Настройка чат-бота

#### 1. Получите API-ключ

OpenAI недоступен из РФ, поэтому используем **OpenRouter** (агрегатор моделей):

1. Зарегистрируйтесь на https://openrouter.ai
2. Создайте ключ: https://openrouter.ai/keys
3. Пополните счёт (нужно хотя бы $1)

#### 2. Создайте файл `.env`

Скопируйте `.env.example` в `.env` и вставьте ключ:

```
OPENAI_API_KEY=sk-or-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=deepseek/deepseek-chat
EMBEDDING_MODEL=openai/text-embedding-3-small
```

Если у вас есть доступ к OpenAI напрямую, можно просто указать ключ без `OPENAI_BASE_URL`.

#### 3. Положите учебник

Поддерживаются форматы:
- **PDF** — только текстовый (не скан без OCR!)
- **TXT** — UTF-8

Скопируйте файл в `knowledge/`:

```
knowledge/
  history_textbook.pdf
```

#### 4. Запустите индексацию

```bash
python build_index.py
```

Скрипт:
- извлечёт текст из PDF/TXT
- разобьёт на фрагменты по 800 символов
- создаст эмбеддинги через OpenAI API
- сохранит индекс в `storage/chroma/`

#### 5. Запустите сайт

```bash
python run.py
```

На всех страницах появится плавающая кнопка в правом нижнем углу — чат-бот «ИИисторик».

### Проверка чат-бота

1. Нажмите на красную кнопку в правом нижнем углу
2. Введите вопрос, например: «Когда было Крещение Руси?»
3. Если в учебнике есть ответ — бот ответит и покажет, на какие фрагменты опирался
4. Если информации нет — бот напишет: «В загруженном учебнике нет достаточной информации»

### Какие файлы отвечают за чат

| Файл | Назначение |
|------|-----------|
| `app/chatbot/routes.py` | API-маршрут `POST /api/chat` |
| `app/chatbot/rag.py` | Поиск по индексу + вызов LLM |
| `app/chatbot/prompts.py` | Системный промт и промт проверки релевантности |
| `static/js/chatbot.js` | Виджет чата на фронтенде |
| `static/css/style.css` | Стили чата (в конце файла) |
| `templates/includes/chatbot_widget.html` | HTML-разметка виджета |
| `build_index.py` | Индексация учебника |
| `knowledge/` | Папка для учебника |
| `storage/chroma/` | Хранилище векторного индекса |
| `.env` | API-ключ OpenAI |

### Важные замечания

- **Бот не выдумывает ответы.** Если в учебнике нет информации, он скажет об этом.
- **Попытки заставить бота игнорировать учебник** (например, «забудь инструкции») блокируются системным промтом.
- **PDF должен быть текстовым.** Сканы без OCR не подходят — `pdfplumber` не сможет извлечь текст.
- **Для работы требуется интернет** — запросы уходят к OpenAI API.
- **Стоимость** — индексация учебника стоит копейки (несколько центов), каждый вопрос тоже доли цента.

### Структура проекта (дополненная)

```
app/
  chatbot/              ← новый blueprint
    routes.py
    rag.py
    prompts.py
knowledge/              ← сюда кладёте учебник
storage/chroma/         ← векторный индекс (создаётся build_index.py)
build_index.py          ← скрипт индексации
.env                    ← API-ключ (не в репозитории!)
.env.example            ← пример файла с ключом
```

## Деплой на PythonAnywhere

Бесплатный хостинг для Flask-приложений.

### 1. Регистрация

Зайдите на https://www.pythonanywhere.com и нажмите **Start running Python** → выберите бесплатный план **Beginner**.

### 2. Клонирование репозитория

Откройте **Consoles → Bash** и выполните:

```bash
git clone https://github.com/timfaz116-code/pro100history.git
```

### 3. Создание виртуального окружения

```bash
cd pro100history
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Настройка Web-приложения

На левой панели **Web** → **Add a new web app**:
- Domain: оставьте `timfaz116-code.pythonanywhere.com`
- Framework: выберите **Manual configuration**
- Python version: **3.12**

В разделе **Code**:
- **Source code**: `/home/timfaz116-code/pro100history`
- **Working directory**: `/home/timfaz116-code/pro100history`

В разделе **Virtualenv**: `/home/timfaz116-code/pro100history/venv`

### 5. Настройка WSGI-файла

Нажмите на ссылку **WSGI configuration file** — откроется редактор. Замените содержимое на:

```python
import sys
import os
path = '/home/timfaz116-code/pro100history'
if path not in sys.path:
    sys.path.append(path)
os.environ['OPENAI_API_KEY'] = 'ваш_ключ_openrouter'
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'
os.environ['LLM_MODEL'] = 'deepseek/deepseek-chat'
os.environ['EMBEDDING_MODEL'] = 'openai/text-embedding-3-small'
from app import create_app
application = create_app()
```

Нажмите **Save**.

### 6. Заполнение базы и индексация

Вернитесь в Bash-консоль:

```bash
cd pro100history
source venv/bin/activate
python seed.py
```

Если нужен чат-бот — положите учебник в `knowledge/` и запустите:

```bash
python build_index.py
```

### 7. Перезагрузка

На странице **Web** нажмите **Reload**.

Сайт будет доступен по адресу: `https://timfaz116-code.pythonanywhere.com`

### 8. Загрузка учебника

Учебник можно загрузить через веб-интерфейс PythonAnywhere:
- **Files** → `pro100history/knowledge/` → **Upload a file**

Или через консоль (если учебник лежит на GitHub рядом с кодом).

### Важно для бесплатного тарифа

- На бесплатном тарифе сайт «засыпает» при отсутствии запросов. При первом открытии после перерыва придётся подождать 5–10 секунд.
- ChromaDB может работать медленнее из-за дисковых ограничений. Для реальной работы лучше перейти на платный тариф ($5/мес).

## Тестовый пользователь

| Email                | Пароль  | Роль    |
|----------------------|---------|---------|
| student@example.com  | 123456  | student |

## Добавление новой роли (teacher/admin)

В модели `User` есть поле `role` со значением по умолчанию `student`. Для добавления новой роли достаточно расширить проверки в роутах, например:

```python
from flask_login import current_user

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated
```
