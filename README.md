# FastAPI AuthN and AuthZ

REST API сервис аутентификации и авторизации на FastAPI с JWT и SQLite.

## Требования

- Python 3.10+

## Установка и запуск

## 1. Клонировать репозиторий и перейти в папку
```bash
git clone https://github.com/MelWerdna/FastAPI-Authz-Authn.git
```

## 2. Создать и активировать виртуальное окружение
```bash
python -m venv .venv
.venv\Scripts\activate # Windows
# source .venv/bin/activate   # Linux/macOS
```       


## 3. Установить зависимости
```bash
pip install -r requirements.txt
```

## 4. Создать файл .env

**.env:**
```env
JWT_SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=db.sqlite3
```
## 5. Запустить сервер

```bash
uvicorn src.main:app --reload
```

SWAGGER UI: http://127.0.0.1:8000

# Запуск через Docker

В проекте есть `Dockerfile` и `docker-compose.yml`, можно запустить сервис в контейнере:

```bash
docker compose up --build
```

После старта приложение будет доступно по тому же адресу:

http://127.0.0.1:8000

