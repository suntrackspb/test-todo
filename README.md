# Notes App

Веб-заметки в стиле Notion: дерево проектов, заметки с rich-text редактором,
todo со статусами, вставка изображений (с устройства и из буфера обмена),
рисование от руки и календарь.

Стек: FastAPI + SQLAlchemy + SQLite (бэкенд), Vue 3 + Vite + Pinia + Tiptap (фронтенд).

## Запуск через Docker (рекомендуется)

```bash
docker compose up -d --build

# добавить пользователя внутри контейнера бэкенда
docker compose exec backend python manage.py create-user <login> <password> ["Имя"]
```

Приложение будет доступно на http://localhost:8080 (nginx отдаёт фронтенд и
проксирует `/api/*` на backend-контейнер). БД и загруженные файлы хранятся в
именованном volume `notes-data`, переживают пересоздание контейнеров.

По умолчанию используется dev-секрет для JWT. Для продакшена задайте свой:

```bash
NOTES_JWT_SECRET=$(openssl rand -hex 32) docker compose up -d --build
```

Остановить: `docker compose down` (данные останутся в volume; `docker compose down -v` удалит и их).

### Выставить наружу по домену (HTTPS)

Контейнер `frontend` слушает только `127.0.0.1:8080`. Чтобы отдать приложение
по домену с HTTPS, поставьте перед ним nginx на хосте — пример конфига:
[deploy/nginx.reverse-proxy.example.conf](deploy/nginx.reverse-proxy.example.conf).

## Backend (без Docker)

```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# добавить пользователя (регистрации в UI нет — пользователи заводятся вручную)
python manage.py create-user <login> <password> ["Отображаемое имя"]
python manage.py list-users

uvicorn app.main:app --reload --port 8000
```

Тесты:

```bash
cd backend && source venv/bin/activate && pytest
```

## Frontend (без Docker)

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173, проксирует /api на backend:8000
npm run test      # vitest
npm run build
```

## Заметки по реализации

- JWT: access-токен (24ч) + refresh-токен (14д). Access-токен также принимается
  как `?token=` query-параметр для эндпоинта `/uploads/...`, так как `<img>` не
  может отправлять `Authorization`-заголовок.
- Изображения хранятся на диске в `backend/uploads/<user_id>/...`, в БД — только путь.
- Рисунки от руки экспортируются с canvas в PNG и загружаются как обычное изображение.
- Календарь агрегирует todo и заметки с проставленной `due_date` по всем проектам пользователя.
