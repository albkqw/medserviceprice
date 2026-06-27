# MedServicePrice — Project Summary

Агрегатор цен на медицинские услуги в Казахстане (аналог Aviasales для клиник).
Пользователь вводит название анализа или услуги, видит цены из разных клиник в своём городе, отсортированные по цене.

---

## Стек

| Слой | Технология |
|---|---|
| API | FastAPI, Pydantic v2, Python 3.11 |
| БД | PostgreSQL 16, SQLAlchemy 2.0 async, asyncpg |
| Миграции | Alembic (async, NullPool) |
| Парсинг | httpx async, BeautifulSoup4 |
| Матчинг | rapidfuzz |
| Планировщик | APScheduler 3.x (AsyncIOScheduler) |
| Инфраструктура | Docker Compose |

---

## Структура репозитория

```
med/
├── docker-compose.yml          # API + PostgreSQL
└── backend/
    ├── Dockerfile
    ├── pyproject.toml
    ├── .env
    ├── alembic/                # миграции
    ├── scripts/
    │   └── seed.py             # справочные данные (города, клиники, источники)
    └── app/
        ├── core/               # config, logging, exceptions
        ├── db/                 # engine, Base, TimestampMixin
        ├── models/             # SQLAlchemy модели
        ├── repositories/       # Repository pattern, BaseRepository[T]
        ├── services/           # бизнес-логика
        ├── schemas/            # Pydantic схемы (запрос/ответ)
        ├── routers/            # FastAPI роутеры
        ├── dependencies/       # DI: get_async_session, get_*_service
        ├── parsers/            # парсер-система
        │   └── sources/        # конкретные источники (kdl.py, invitro.py, doq.py)
        ├── normalization/      # нормализация raw_prices → prices
        └── scheduler/          # APScheduler: jobs.py, scheduler.py
```

---

## Data Model

Два слоя данных:

```
[Парсер] → raw_prices (сырые данные, как с сайта)
                ↓
[Нормализация] → prices (структурированные, читает API)
```

### Таблицы

| Таблица | Назначение |
|---|---|
| `cities` | Алматы, Астана, Шымкент |
| `clinics` | Клиника, привязана к городу. UniqueConstraint(name, city_id) |
| `services` | Канонический справочник услуг (`name` + `synonyms` JSONB) |
| `parser_sources` | Источник парсера (slug, base_url, last_parsed_at) |
| `raw_prices` | Сырые данные. Чексумма SHA-256 = дедупликация. `is_processed=false` до нормализации |
| `prices` | Нормализованные цены. Append-only, `is_active` + `parsed_at` для staleness |
| `unmatched_services` | Услуги, которые не удалось привязать к справочнику |
| `parse_runs` | Лог каждого запуска парсера (статус, время, кол-во записей, ошибка) |

### Ключевые решения
- `raw_prices.checksum` UNIQUE — дедупликация без SELECT перед INSERT
- `prices` append-only — история цен сохраняется, `is_active=false` при обновлении
- `services.synonyms` JSONB с GIN индексом — синонимы для поиска
- Цены старше 30 дней исключаются из поиска (`parsed_at >= now() - 30 days`)
- `clinics` UniqueConstraint(name, city_id) — защита от дублей при повторном seed

---

## API Endpoints

```
GET  /api/v1/health
GET  /api/v1/cities
GET  /api/v1/clinics?city_slug=almaty
GET  /api/v1/clinics/{id}
GET  /api/v1/services?query=анализ&category=lab
GET  /api/v1/services/{id}
GET  /api/v1/search?query=анализ&city_slug=almaty&min_price=0&max_price=5000

GET  /api/v1/scheduler/jobs
POST /api/v1/scheduler/run/{slug}
GET  /api/v1/scheduler/runs?source=kdl&limit=50
GET  /api/v1/scheduler/runs/{run_id}
```

### Как работает поиск

1. Найти `Service` записи где `name ILIKE %query%` или `synonyms ILIKE %query%`
2. Одним `IN (uuid1, uuid2, ...)` запросом получить все цены по найденным сервисам
3. Отсортировать по цене

Итого: 2 запроса к БД, без N+1.

---

## Парсер-система

```
BaseParser          абстрактный класс, метод parse() → list[ParsedItem]
HttpClient          async httpx, retry × 3, задержка между запросами
storage.save_items  INSERT + ON CONFLICT DO NOTHING по чексумме
runner.py           CLI: python -m app.parsers.runner <slug> [--dry-run]
```

### Источники

| slug | Сайт | Метод | Городов | Записей в БД |
|---|---|---|---|---|
| `kdl` | kdlolymp.kz | JSON API | 3 | ~4 910 |
| `invitro` | invitro.kz | HTML (BeautifulSoup) | 3 | ~6 370 |
| `doq` | doq.kz | JSON API | 3 | ~16 534 |

### Добавить новый источник
1. Создать `app/parsers/sources/<slug>.py`, унаследоваться от `BaseParser`
2. Добавить в `_PARSERS` в `app/parsers/runner.py` и `app/scheduler/jobs.py`
3. Добавить в `SOURCE_DEFAULT_CATEGORY` в `app/normalization/runner.py`
4. Добавить в `_JOBS` в `app/scheduler/scheduler.py`
5. Запустить `python -m app.parsers.runner <slug>`

---

## Нормализация

Процесс: `raw_prices` (is_processed=False) → `prices` + `unmatched_services`

### Матчинг (3 уровня)

```
1. Exact / synonym   O(1)   dict по normalize_text() — lowercase + collapse whitespace
2. Fuzzy             O(N)   rapidfuzz token_sort_ratio, порог 85%
3. Unmatched                → unmatched_services, suggested_service_id если score ≥ 60%
```

### Bootstrap clinics (для DOQ и новых источников)

Перед нормализацией `_bootstrap_clinics()` автоматически создаёт `Clinic` записи
из уникальных `raw_clinic_name` (формат: `"Название (Город)"`), привязывая к city_id.

### Запуск

```bash
# Первый раз: создать canonical Services из уникальных raw-имён
python -m app.normalization.runner --source kdl --bootstrap

# Повторный запуск
python -m app.normalization.runner --source kdl
```

---

## Планировщик (APScheduler)

Запускается автоматически при старте FastAPI (lifespan).

### Расписание (Asia/Almaty)

| Источник | Время |
|---|---|
| KDL | 02:00 |
| ИНВИТРО | 03:00 |
| DOQ | 04:00 |

### Ретраи

До 3 попыток. Задержки: 60с → 120с между попытками.
Каждая попытка — отдельная запись в `parse_runs`.

### API

```
GET  /api/v1/scheduler/jobs              # список задач и next_run_time
POST /api/v1/scheduler/run/{slug}        # ручной запуск (202, фоновый)
GET  /api/v1/scheduler/runs?source=kdl   # лог запусков
GET  /api/v1/scheduler/runs/{run_id}     # детали запуска
```

---

## Текущее состояние БД

| Таблица | Записей |
|---|---|
| cities | 3 |
| clinics | 645 |
| services | 5 008 |
| raw_prices | 27 814 |
| prices | 27 814 |
| unmatched_services | 0 |

---

## Запуск

### Локально (для скриптов)

```bash
cd backend
python -m scripts.seed
python -m app.parsers.runner kdl --dry-run
python -m app.normalization.runner --source kdl --bootstrap
```

### В Docker (для API)

```bash
docker compose up --build

# Первоначальное наполнение БД
docker compose exec api python -m scripts.seed
docker compose exec api python -m app.parsers.runner kdl
docker compose exec api python -m app.parsers.runner invitro
docker compose exec api python -m app.parsers.runner doq
docker compose exec api python -m app.normalization.runner --source kdl --bootstrap
docker compose exec api python -m app.normalization.runner --source invitro --bootstrap
docker compose exec api python -m app.normalization.runner --source doq --bootstrap
```

### Ручной запуск парсера через API

```bash
curl -X POST http://localhost:8000/api/v1/scheduler/run/kdl

# Посмотреть логи
curl http://localhost:8000/api/v1/scheduler/runs?source=kdl
```

---

## Что осталось сделать

### Высокий приоритет

- [ ] Фронтенд (React / Next.js) — поиск, фильтры, карточки клиник
- [ ] README с инструкцией запуска

### Средний приоритет

- [ ] Пагинация в `/api/v1/search` (добавить `offset`)
- [ ] `GET /api/v1/clinics/{id}/services` — карточка клиники со всеми услугами
- [ ] Admin UI для `unmatched_services`
- [ ] Staleness pipeline — деактивировать `prices.is_active=false`
- [ ] Тесты — matcher, pipeline, search_service

### Дополнительные функции (дают баллы по ТЗ)

- [ ] Карта клиник (Leaflet)
- [ ] История изменения цен
- [ ] Сравнение клиник в режиме таблицы
- [ ] Подписка на изменение цены
