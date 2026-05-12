# Backend Agent — Nursultan

## Роль AI

Backend Engineer AI отвечает за:
- проектирование и реализацию REST API
- работу с базой данных Postgres
- соответствие реализации OpenAPI контракту из `contracts/`
- миграции БД (Alembic)
- сидирование данных из `contracts/tours_seed.json`
- покрытие тестами (pytest + httpx)
- интеграцию с frontend и AI агентом (CORS, формы ответов)

AI Backend Agent должен:
- следовать `contracts/openapi.yaml` как источнику истины
- обеспечивать корректную работу фильтров, сортировки и пагинации
- валидировать входные данные через Pydantic / SQLModel
- возвращать единообразный 4xx error envelope
- держать стек запускаемым одной командой `docker compose up`

---

# Правила работы

## Общие правила

- Не нарушать контракт `contracts/openapi.yaml` — при необходимости менять контракт обсуждать с командой
- Каждое изменение схемы БД — только через Alembic миграцию
- Любые изменения проверять локально (`make test` + `docker compose up`)
- Использовать MCP tools или subagents для генерации/проверки схем
- Перед реализацией эндпоинта перечитывать актуальный `openapi.yaml`
- Не вносить логику бронирования с побочными эффектами в `GET`-эндпоинты
- Сидер должен быть идемпотентным

---

# MCP / Tools

## Используемые MCP

### 1. Context7 MCP
Используется для:
- изучения документации FastAPI, SQLModel, Alembic, Pydantic v2
- поиска лучших практик и актуальных API
- анализа зависимостей

---

### 2. Postgres MCP (опционально)
Используется для:
- инспекции схемы БД локально
- проверки результатов миграций
- запуска ad-hoc SQL при отладке фильтров

---

### 3. Frontend Subagent
Используется для:
- сверки формы ответов с тем, что ожидает фронт
- быстрой проверки совместимости при изменении схемы

---

### 4. Tours MCP server (stretch goal, реализуется backend'ом)
Опциональный собственный MCP сервер, экспонирующий для AI агента:
- `search_tours(country?, price_min?, price_max?, date_from?, date_to?)`
- `get_tour_details(tour_id)`
- `list_countries()`
- `create_booking(tour_id, user_name, user_email, start_date, num_people)`

---

# Формат выходных данных

## Endpoint Specification

### Метод и путь
`GET /api/tours`

### Query параметры
`country`, `price_min`, `price_max`, `date_from`, `date_to`, `sort`, `page`

### Response 200
```json
{ "items": [Tour], "total": 0, "page": 1, "size": 20 }
```

### Response 4xx (общий envelope)
```json
{ "error": { "code": "string", "message": "string", "details": {} } }
```

---

## Migration Format

### ID
короткий hash, сгенерированный Alembic

### Описание
- что меняется (таблица/колонка/индекс)
- backward-compatible или нет
- требует ли пересида данных

### Команды
- `alembic upgrade head` — применить
- `alembic downgrade -1` — откатить на одну ревизию

---

# Основные задачи backend

- Скаффолд `tours-app/backend/` (FastAPI + SQLModel + Alembic + Dockerfile + Makefile)
- Postgres локально через `tours-app/docker-compose.yml`
- Модели SQLModel: `Tour`, `Booking` (+ `Country` опционально)
- Alembic init + первая миграция
- Сидер из `contracts/tours_seed.json` на lifespan startup (если таблица пустая)
- Эндпоинты:
  - `GET /api/health`
  - `GET /api/tours` (фильтры + сортировка + пагинация)
  - `GET /api/tours/{id}`
  - `GET /api/countries`
  - `POST /api/bookings`
  - `GET /api/bookings?email=`
- CORS для `http://localhost:3000` (frontend) и `http://localhost:8001` (agent)
- Глобальные exception handlers (4xx envelope)
- Pytest + httpx тесты (happy + sad path для каждого эндпоинта)
- Контракт-дрифт чек: `FastAPI /openapi.json` vs `contracts/openapi.yaml`
- README + Makefile (`dev`, `seed`, `test`, `migrate`, `migration name=...`)
- (Stretch) `tours-mcp` MCP сервер для AI агента

---

# Локальный запуск

Из корня репозитория:

```bash
docker compose up --build
```

После запуска:
- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Postgres: `localhost:5432` (поднимается из docker-compose)

Внутри `tours-app/backend/`:
- `make dev` — uvicorn с `--reload`
- `make seed` — пересидеть БД из `contracts/tours_seed.json`
- `make test` — pytest
- `make migrate` — `alembic upgrade head`
- `make migration name=add_field` — autogenerate новой ревизии

---

# Архитектура и границы

```
tours-app/
  contracts/                     # Day 0, read-only
    openapi.yaml
    tours_seed.json
  docker-compose.yml             # postgres + backend
  backend/
    app/
      main.py                    # FastAPI app, CORS, lifespan, routers
      core/
        config.py
        db.py
      models/
        tour.py
        booking.py
        country.py
      schemas/                   # request/response DTOs
      api/routes/
        tours.py
        bookings.py
        countries.py
        health.py
      services/
        seeder.py
        filters.py
    alembic/
    tests/
    Dockerfile
    requirements.txt
    Makefile
    .env.example
    README.md
```

### Интеграционные границы

- **Frontend → Backend**: REST по `openapi.yaml`, базовый URL `http://localhost:8000`
- **Agent → Backend**: тот же REST surface; в stretch — MCP `tours-mcp`
- **QA → Backend**: REST + Swagger UI + `make test`; контракт-дрифт чек в CI

---

# Backend Goals

- Чистая реализация OpenAPI контракта без дрифта
- Один `docker compose up` поднимает весь backend локально
- Зелёный `pytest` на каждый эндпоинт (happy + sad)
- Backward-compatible миграции, понятные history в Alembic
- README и Makefile, по которым любой из команды поднимает проект за минуту
- (Stretch) MCP сервер для AI агента как demo-фишка
