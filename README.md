<div align="center">

<img src="./RuDart.svg" alt="RuDapt" width="420" />

# Startup Localization AI

**Бери свежие стартапы из США. Запускай локально в любом регионе РФ.**

RuDapt подтягивает проекты с **Product Hunt** и **Y Combinator**, и за минуту собирает
production-ready бизнес-план их локализации в выбранный субъект РФ —
с MVP, юнит-экономикой, конкурентами, регуляторикой и 90-дневным roadmap.

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![Backend](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](#)
[![Frontend](https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white)](#)
[![DB](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](#)
[![AI](https://img.shields.io/badge/Claude-Opus_4.7-D97757?logo=anthropic&logoColor=white)](#)
[![License](https://img.shields.io/badge/license-MIT-22c55e)](#license)

</div>

---

## ✨ Что умеет

| | |
|---|---|
| ⚡ **Свежие стартапы каждый день** | Парсер тянет Product Hunt (GraphQL/RSS) и Y Combinator каталог по cron |
| 🎯 **85 регионов РФ** | Учитывает покупательную способность, налоговые особенности, локальных конкурентов |
| 🧠 **Двойной LLM** | Anthropic Claude Opus 4.7 (с prompt caching ≈ −70% токенов) или OpenAI GPT-4o |
| 📊 **Структурированный отчёт** | JSON-схема + красивый Markdown: суть, MVP, конкуренты, каналы, юнит-экономика, регуляторика, риски, roadmap |
| 🔐 **Готовая авторизация** | JWT access + refresh, личный кабинет, история отчётов |
| 🚀 **Production-ready** | Docker Compose, Alembic миграции, ARQ воркеры, GitHub Actions CI |

---

## 🏗 Архитектура

```
┌─────────────┐      HTTPS       ┌──────────────────┐
│  Next.js 14 │ ───────────────► │  FastAPI (REST)  │
│  TanStack Q │ ◄─────────────── │   Pydantic v2    │
└─────────────┘                   └────────┬─────────┘
                                           │
            ┌──────────────────────────────┼──────────────────────────────┐
            │                              │                              │
            ▼                              ▼                              ▼
     ┌────────────┐               ┌──────────────┐                 ┌──────────────┐
     │ PostgreSQL │               │    Redis     │                 │   LLM API    │
     │  (SQLA 2)  │               │ queue/cache  │                 │ Anthropic /  │
     └────────────┘               └──────┬───────┘                 │   OpenAI     │
                                         │                         └──────────────┘
                                         ▼
                                  ┌──────────────┐
                                  │ ARQ workers  │
                                  │  ingest +    │
                                  │  generate    │
                                  └──────┬───────┘
                                         ▼
                              Product Hunt · Y Combinator
```

**Поток генерации.** UI отправляет `POST /api/generate-plan {startup_id, region}` →
backend создаёт запись `Report(status=pending)`, ставит job в очередь, мгновенно возвращает
`report_id`. Воркер собирает системный промт + контекст стартапа → LLM → парсит JSON →
сохраняет план в `reports.content` (статус `done`). Фронт поллит `GET /api/reports/{id}`.

---

## 🧰 Стек

**Backend:** Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2 ·
ARQ · httpx · feedparser · Anthropic SDK · OpenAI SDK · python-jose · passlib

**Frontend:** Next.js 14 (App Router) · TypeScript · TailwindCSS · Radix UI ·
TanStack Query · react-markdown · lucide-react

**Infra:** Docker Compose · PostgreSQL 15 · Redis 7 · GitHub Actions

---

## 📁 Структура

```
.
├── backend/                  FastAPI + воркеры
│   ├── app/
│   │   ├── api/              маршруты (auth, startups, reports)
│   │   ├── models/           SQLAlchemy: User, Startup, Report
│   │   ├── schemas/          Pydantic DTO
│   │   ├── services/
│   │   │   ├── llm.py        Anthropic/OpenAI клиент + prompt caching
│   │   │   ├── prompt.py     системный промт + сборка контекста
│   │   │   ├── markdown.py   рендер JSON → Markdown
│   │   │   └── scraper/      Product Hunt + YC + runner
│   │   └── workers/          ARQ: ingest (cron) + generate
│   └── alembic/versions/     миграции БД
├── frontend/                 Next.js
│   └── src/
│       ├── app/              (auth) | (app) роуты
│       ├── components/       StartupCard, RegionPickerDialog, ui/*
│       └── lib/              api, regions (85 субъектов РФ)
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## 🚀 Быстрый старт

### 1. Клонировать и настроить env

```bash
git clone https://github.com/<your>/rudapt.git
cd rudapt
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

В `.env` задай минимум `JWT_SECRET` и один из ключей: `ANTHROPIC_API_KEY` или `OPENAI_API_KEY`.

### 2. Поднять backend через Docker

```bash
docker compose up -d postgres redis backend worker
```

Это:
- поднимет Postgres и Redis;
- применит Alembic миграции;
- запустит FastAPI на `http://localhost:8000` (Swagger: `/docs`);
- запустит ARQ-воркер. На старте он сразу запустит парсер стартапов.

### 3. Запустить frontend

```bash
cd frontend
npm install
npm run dev
```

Открой `http://localhost:3000` → зарегистрируйся → лента → выбери стартап → регион → план.

---

## 🔑 Переменные окружения

| key | назначение |
|---|---|
| `DATABASE_URL` | postgres+asyncpg DSN |
| `REDIS_URL` | redis для ARQ и refresh-кеша |
| `JWT_SECRET` | подпись JWT (генерируй `openssl rand -hex 32`) |
| `ANTHROPIC_API_KEY` | основной LLM-провайдер (Claude Opus 4.7) |
| `OPENAI_API_KEY` | фолбэк (GPT-4o) |
| `LLM_PROVIDER` | `anthropic` (по умолчанию) или `openai` |
| `PRODUCTHUNT_TOKEN` | опционально — без него используется RSS |
| `CORS_ORIGINS` | список origin'ов через запятую |

---

## 🔌 API

| метод | путь | назначение |
|---|---|---|
| `POST` | `/api/auth/register` | регистрация, возвращает токены |
| `POST` | `/api/auth/login` | логин |
| `POST` | `/api/auth/refresh` | обновить access-токен |
| `GET`  | `/api/auth/me` | текущий пользователь |
| `GET`  | `/api/startups?q=&source=&category=&limit=&offset=` | лента |
| `GET`  | `/api/startups/{id}` | детали стартапа |
| `POST` | `/api/generate-plan` | поставить задачу генерации (202 Accepted) |
| `GET`  | `/api/reports` | мои планы |
| `GET`  | `/api/reports/{id}` | план + статус |
| `GET`  | `/health` | health check |

Полное описание — Swagger UI на `/docs`.

---

## 🧪 Дев-команды

```bash
# Backend
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python -c "from app.workers.ingest import ingest_startups"

# Frontend
cd frontend && npm run dev          # dev server
cd frontend && npm run typecheck    # проверка типов
cd frontend && npm run build        # production build
```

---

## 🗺 Roadmap

- [ ] Экспорт отчёта в PDF (puppeteer)
- [ ] Crunchbase интеграция
- [ ] Сравнение нескольких регионов в одном плане
- [ ] Stripe/ЮKassa подписки (Pro план)
- [ ] Telegram-бот с уведомлениями о свежих стартапах в выбранных категориях
- [ ] Public API + ключи

---

## 📄 License

MIT © 2026 Andrew Dumin
