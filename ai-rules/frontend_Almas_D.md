# Отчёт: Frontend Developer — Алмас Д.

## Роль и вклад

- **Роль**: Frontend Developer (UI/UX + полная клиентская часть турагенства в каталоге `frontend`).
- **Проект**: платформа подбора и бронирования туров (список → фильтры → карточка → форма брони → «Мои брони» → опционально AI-чат).
- **Стек**: Angular (standalone), HTML-шаблоны, SCSS, TypeScript, Tailwind CSS v4 (CSS-first `@theme`), окружения dev/prod.

## Что сделано по функционалу

| Область | Результат |
|---------|-----------|
| Маршруты | `/` каталог, `/tours/:id` деталь + бронь, `/my-bookings` по email, `**` 404 |
| API по контракту с бэком | `GET /api/tours`, `GET /api/tours/{id}`, `GET /api/countries`, `POST /api/bookings`, `GET /api/bookings?email=`, `POST /api/agent/chat` — имена полей как в `backend.md` (`price_usd`, `tour_id`, `session_id`, и т.д.) |
| Автономность до бэка | Режим моков через сервисы + seed-данные в коде; переключение `environment.useMocks` / `apiUrl` |
| UI/UX | Редакционный «travel» стиль, без градиентов, адаптив, skip-link, фокус, типографика Fraunces + Source Sans 3 |
| AI | Виджет чата, `sessionStorage` для `session_id`, ответы с `suggested_tour_ids` и ссылки на туры |

## MCP (Model Context Protocol)

| MCP | Зачем использовал |
|-----|-------------------|
| **Context7** | Актуальная документация по Angular (standalone, signals, роутинг, практики) и по Tailwind v4 (`@theme`, утилиты); сверка перед принятием архитектурных решений |

*Примечание для защиты*: Playwright / другие MCP в команде могли использовать QA или другие роли; во frontend-потоке основным документным MCP был Context7.

## Агенты и правила в Cursor

| Что подключал / использовал | Назначение |
|-----------------------------|------------|
| Файл **`frontend/ui-ux-designer.agent.md`** | Правила для «дизайн-критика»: UX, доступность, иерархия, без «generic SaaS» |
| Файл **`frontend/frontend-agent.md`** | Правила для фронтенд-архитектуры: Angular, структура фич, тесты, интеграция с API |
| **Subagents в Cursor** (разово при планировании) | Отдельные запросы агентам explore/generalPurpose под UI/UX направление и под технический скелет приложения — чтобы разделить дизайн и код-план |

Дополнительно опирался на **`backend.md`** в корне репозитория как на описание REST и ошибок.

## Модель и режим в Cursor

- Работа велась в **Cursor**, режим **Agent** (автоматические правки файлов, терминал, сборка).
- **Точное имя модели в выпадающем списке Cursor** укажи перед защитой по своему скриншоту чата (меню выбора модели над полем ввода): там же видно, что именно было активно при коммитах/записи демо.

## Верификация

- Сборка: `npm run build` в каталоге `frontend`.
- Юнит-тесты: `npm test` (Vitest через Angular CLI).

## Структура кода (кратко)

- `src/app/core/` — модели API, HTTP-сервисы, `SessionIdService`, мок-слой.
- `src/app/features/` — страницы туров, детали, брони, 404.
- `src/app/shared/` — `TourCard`, `FilterPanel`, `ChatWidget`.
- `src/environments/` — `apiUrl`, `useMocks`, prod-замена через `angular.json`.

## Рефлексия для workflow (1–2 строки)

- ИИ ускорил скаффолд Angular + Tailwind и типизацию под контракт; руками доводилось согласование полей с бэком и проверка сборки/шаблонов.
- Риск дрифта API снимался жёстким следованием `backend.md` и единым naming в TypeScript.

---

