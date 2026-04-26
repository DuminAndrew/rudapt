<div align="center">

<a href="https://github.com/DuminAndrew/rudapt">
  <img src=".github/assets/hero.svg" alt="RuDapt — Startup Localization AI" width="100%" />
</a>

<br/>

<p align="center">
  <a href="#-quick-start"><img alt="Quick Start" src="https://img.shields.io/badge/⚡-Quick%20Start-8B5CF6?style=for-the-badge&labelColor=0B0F1F"/></a>
  <a href="#-api"><img alt="API Reference" src="https://img.shields.io/badge/📡-API%20Reference-06B6D4?style=for-the-badge&labelColor=0B0F1F"/></a>
  <a href="#-architecture"><img alt="Architecture" src="https://img.shields.io/badge/🏗-Architecture-F43F5E?style=for-the-badge&labelColor=0B0F1F"/></a>
  <a href="#-roadmap"><img alt="Roadmap" src="https://img.shields.io/badge/🗺-Roadmap-F97316?style=for-the-badge&labelColor=0B0F1F"/></a>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square"/>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-14-000?style=flat-square&logo=nextdotjs"/>
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript&logoColor=white"/>
  <img alt="Postgres" src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
  <img alt="Redis" src="https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white"/>
  <img alt="Anthropic" src="https://img.shields.io/badge/Anthropic-Claude%20Opus%204.7-D97757?style=flat-square&logo=anthropic"/>
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white"/>
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img alt="CI" src="https://github.com/DuminAndrew/rudapt/actions/workflows/ci.yml/badge.svg?style=flat-square"/>
</p>

<h3>
  Бери свежие стартапы из США.<br/>
  Запускай локально <em>в любом регионе РФ</em>.
</h3>

<p align="center" style="max-width:680px;margin:0 auto;">
  <strong>RuDapt</strong> — это SaaS-платформа, которая каждый день парсит&nbsp;
  <a href="https://www.producthunt.com">Product Hunt</a> и&nbsp;
  <a href="https://www.ycombinator.com">Y&nbsp;Combinator</a>,
  и за минуту собирает production-ready бизнес-план локализации
  выбранного стартапа в выбранный субъект РФ —
  с MVP, юнит-экономикой, конкурентами, регуляторикой и 90-дневным roadmap.
</p>

</div>

---

## 📑 Содержание

- [✨ Возможности](#-возможности)
- [🎬 Как это работает](#-как-это-работает)
- [🏗 Архитектура](#-архитектура)
- [🧰 Стек](#-стек)
- [⚡ Quick Start](#-quick-start)
- [🔑 Переменные окружения](#-переменные-окружения)
- [📡 API](#-api)
- [📁 Структура проекта](#-структура-проекта)
- [🧪 Команды разработчика](#-команды-разработчика)
- [🗺 Roadmap](#-roadmap)
- [📄 License](#-license)

---

## ✨ Возможности

<table>
<tr>
<td width="33%" valign="top">

### ⚡ Свежий поток
Парсер идёт в **Product Hunt** (GraphQL/RSS) и **Y Combinator** по cron, кладёт в БД с дедупликацией. Лента с фильтрами по источнику, категориям и поиском.

</td>
<td width="33%" valign="top">

### 🎯 85 регионов РФ
От Москвы до Якутии. Промт учитывает покупательную способность, локальных конкурентов, налоговый режим, ФЗ-152 и доступные сервисы (ЮKassa, Yandex Cloud, VK Ads).

</td>
<td width="33%" valign="top">

### 🧠 Двойной LLM
**Anthropic Claude Opus 4.7** как основной, с **prompt caching** (–70% токенов на системный промт). **OpenAI GPT-4o** как фолбэк через `LLM_PROVIDER`.

</td>
</tr>
<tr>
<td valign="top">

### 📊 Структурированный план
JSON-схема: `summary`, `value_prop_ru`, `mvp`, `competitors_ru`, `channels`, `unit_economics`, `regulatory`, `risks`, `roadmap_90d`. + красивый Markdown-рендер для чтения и экспорта.

</td>
<td valign="top">

### 🔐 Auth из коробки
JWT access + refresh, регистрация, логин, личный кабинет с историей отчётов. Pro-план с квотами на генерации (заготовка под подписки).

</td>
<td valign="top">

### 🚀 Production-ready
Docker Compose всё поднимает одной командой. Alembic миграции, ARQ-воркеры, асинхронная генерация, GitHub Actions CI: lint + миграции + typecheck + build + docker.

</td>
</tr>
</table>

---

## 🎬 Как это работает

```mermaid
sequenceDiagram
    autonumber
    participant U as Пользователь
    participant FE as Next.js
    participant API as FastAPI
    participant DB as Postgres
    participant Q as Redis Queue
    participant W as ARQ Worker
    participant LLM as Claude / GPT-4o

    U->>FE: Выбирает стартап + регион РФ
    FE->>API: POST /api/generate-plan
    API->>DB: INSERT report(status='pending')
    API->>Q: enqueue("generate_report", id)
    API-->>FE: 202 Accepted {report_id}
    FE-->>U: Перенаправление на /reports/{id}

    Note over W: Воркер просыпается
    W->>DB: SELECT startup, report
    W->>LLM: SYSTEM (cached) + USER (startup + region)
    LLM-->>W: JSON business plan
    W->>DB: UPDATE report(status='done', content, content_md)

    loop Polling
        FE->>API: GET /api/reports/{id}
        API-->>FE: status, content, markdown
    end
    FE-->>U: Готовый бизнес-план
```

---

## 🏗 Архитектура

```
┌──────────────────┐     HTTPS      ┌─────────────────────┐
│   Next.js 14     │ ─────────────► │     FastAPI         │
│   App Router     │ ◄───────────── │   Pydantic v2       │
│   TanStack Query │                │   SQLAlchemy 2.0    │
└──────────────────┘                └──────────┬──────────┘
                                               │
            ┌──────────────────────────────────┼──────────────────────────────┐
            │                                  │                              │
            ▼                                  ▼                              ▼
   ┌────────────────┐                ┌─────────────────┐              ┌────────────────┐
   │  PostgreSQL 15 │                │     Redis 7     │              │     LLM API    │
   │   users · ⋯    │                │  queue + cache  │              │   Anthropic /  │
   │ startups · ⋯   │                └────────┬────────┘              │     OpenAI     │
   │   reports · ⋯  │                         │                       └────────────────┘
   └────────────────┘                         ▼
                                     ┌────────────────┐
                                     │   ARQ Worker   │
                                     │ ingest (cron)  │
                                     │   generate     │
                                     └───────┬────────┘
                                             ▼
                              Product Hunt · Y Combinator API/RSS
```

---

## 🧰 Стек

| Слой | Технологии |
|---|---|
| **Frontend** | Next.js 14 · TypeScript · TailwindCSS · Radix UI · TanStack Query · react-markdown · lucide-react |
| **Backend** | Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2 · python-jose · passlib |
| **Workers** | ARQ (async-native) · httpx · feedparser · tenacity |
| **AI** | Anthropic SDK (Claude Opus 4.7 + prompt caching) · OpenAI SDK (GPT-4o, JSON mode) |
| **Data** | PostgreSQL 15 · Redis 7 |
| **DevOps** | Docker Compose · Alembic · GitHub Actions |

---

## ⚡ Quick Start

> **Требования:** Docker Desktop с включённой виртуализацией (`VT-x` / `AMD-V` в BIOS, `Hyper-V` или `WSL2` в Windows). Для дев-режима фронта — Node.js 20+.

```bash
# 1. Клонировать
git clone https://github.com/DuminAndrew/rudapt.git
cd rudapt

# 2. Настроить окружение
cp .env.example .env
cp frontend/.env.example frontend/.env.local
#   ↑ впиши JWT_SECRET и хотя бы один из ANTHROPIC_API_KEY / OPENAI_API_KEY

# 3. Поднять backend (Postgres + Redis + API + Worker)
docker compose up -d

# 4. Запустить frontend dev
cd frontend && npm install && npm run dev
```

Открой:
- **http://localhost:3000** — UI
- **http://localhost:8000/docs** — Swagger API
- **http://localhost:8000/health** — health check

Воркер при старте сразу подтянет свежие стартапы из Product Hunt и YC. Через 1–2 минуты лента наполнится.

---

## 🔑 Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DATABASE_URL` | Postgres async DSN | `postgresql+asyncpg://rudapt:rudapt@postgres:5432/rudapt` |
| `REDIS_URL` | Redis для ARQ и кеша | `redis://redis:6379/0` |
| `JWT_SECRET` | Подпись JWT (`openssl rand -hex 32`) | — обязательно — |
| `ACCESS_TOKEN_TTL_MIN` | TTL access-токена | `60` |
| `REFRESH_TOKEN_TTL_DAYS` | TTL refresh-токена | `30` |
| `ANTHROPIC_API_KEY` | Ключ Anthropic | — |
| `OPENAI_API_KEY` | Ключ OpenAI (фолбэк) | — |
| `LLM_PROVIDER` | `anthropic` или `openai` | `anthropic` |
| `LLM_MODEL_ANTHROPIC` | Модель Claude | `claude-opus-4-7` |
| `LLM_MODEL_OPENAI` | Модель OpenAI | `gpt-4o` |
| `PRODUCTHUNT_TOKEN` | Токен PH (опционально, иначе RSS) | — |
| `CORS_ORIGINS` | Origins через запятую | `http://localhost:3000` |

---

## 📡 API

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/auth/register` | Регистрация → `{access_token, refresh_token}` |
| `POST` | `/api/auth/login` | Логин |
| `POST` | `/api/auth/refresh` | Обновить access по refresh |
| `GET`  | `/api/auth/me` | Текущий пользователь |
| `GET`  | `/api/startups` | Лента: `?q=&source=&category=&limit=&offset=` |
| `GET`  | `/api/startups/{id}` | Детали стартапа |
| `POST` | `/api/generate-plan` | `{startup_id, region}` → 202 + report_id |
| `GET`  | `/api/reports` | Мои планы |
| `GET`  | `/api/reports/{id}` | План со статусом и контентом |
| `GET`  | `/health` | Liveness probe |

Полная схема — Swagger UI на `/docs`.

### Пример запроса

```http
POST /api/generate-plan HTTP/1.1
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "startup_id": "5b3c0b1a-...-...",
  "region": "Татарстан"
}
```

```json
HTTP/1.1 202 Accepted
{
  "id": "r1-uuid",
  "status": "pending",
  "region": "Татарстан",
  "model": null,
  "content": null,
  "created_at": "2026-04-26T10:12:33Z"
}
```

---

## 📁 Структура проекта

```
.
├── backend/                       FastAPI + ARQ
│   ├── app/
│   │   ├── api/                   маршруты (auth, startups, reports)
│   │   ├── models/                User · Startup · Report
│   │   ├── schemas/               Pydantic DTO
│   │   ├── services/
│   │   │   ├── llm.py             Anthropic + OpenAI клиент
│   │   │   ├── prompt.py          системный промт + сборка контекста
│   │   │   ├── markdown.py        JSON → Markdown
│   │   │   └── scraper/           Product Hunt · YC · runner
│   │   └── workers/               arq_app · ingest · generate
│   ├── alembic/versions/          миграции
│   └── Dockerfile
├── frontend/                      Next.js
│   └── src/
│       ├── app/                   (auth) · (app) роуты
│       ├── components/            ui/ · StartupCard · RegionPickerDialog · …
│       └── lib/                   api · regions · utils
├── .github/workflows/ci.yml       CI: backend + frontend + docker build
├── docker-compose.yml
└── README.md
```

---

## 🧪 Команды разработчика

```bash
# Backend
docker compose up -d                                    # поднять стек
docker compose logs -f backend                          # логи API
docker compose logs -f worker                           # логи воркера
docker compose exec backend alembic upgrade head        # миграции
docker compose exec backend alembic revision --autogenerate -m "msg"

# Frontend
cd frontend
npm run dev                                             # http://localhost:3000
npm run typecheck                                       # TS проверка
npm run build                                           # production build
npm run lint                                            # ESLint

# Полная пересборка
docker compose down -v && docker compose up -d --build
```

---

## 🗺 Roadmap

- [ ] **Public API + ключи** — отдельные `/api/v1/*` с rate-limit и API-ключами в ЛК
- [ ] **Сравнение регионов** — несколько субъектов РФ в одном плане, side-by-side
- [ ] **Crunchbase интеграция** — третий источник стартапов
- [ ] **Экспорт в PDF** — отдельный микросервис на Puppeteer
- [ ] **Telegram-бот** — уведомления о свежих стартапах в выбранных категориях
- [ ] **Stripe / ЮKassa подписки** — Pro-план с увеличенными квотами

---

## 📄 License

[MIT](LICENSE) © 2026 [Andrew Dumin](https://github.com/DuminAndrew)

<div align="center">
  <br/>
  <sub>Сделано с ❤️ для русскоязычных предпринимателей, которым лень копировать чужие идеи вручную.</sub>
  <br/><br/>
  <a href="https://github.com/DuminAndrew/rudapt/stargazers">
    <img src="https://img.shields.io/github/stars/DuminAndrew/rudapt?style=social" alt="Stars"/>
  </a>
</div>
