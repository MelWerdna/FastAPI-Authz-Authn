# FastAPI AuthN and AuthZ

REST API сервис аутентификации и авторизации на FastAPI с JWT и SQLite.

## Требования

- Python 3.10+

## Установка и запуск

```bash
# 1. Клонировать репозиторий и перейти в папку
git clone [<repo-url>](https://github.com/MelWerdna/FastAPI-Authz-Authn.git)

# 2. Создать и активировать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать файл .env
```

**.env:**
```env
JWT_SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=db.sqlite3
```

```bash
# 5. Запустить сервер
uvicorn src.main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

Документация API: http://127.0.0.1:8000/docs
