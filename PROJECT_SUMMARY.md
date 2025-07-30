# ERP System Development Summary

## Project Vision
A modular, scalable ERP system built with FastAPI + PostgreSQL, designed for web, mobile, and AI integration. Long-term goal: SaaS platform with customizable modules for SMEs.

## Tech Stack
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Caching & Tasks: Redis + Celery
- Frontend: Swagger UI (testing), Jinja2 (admin), React.js (future)
- AI Integration: OpenAI or LangChain (future)

## Key Decisions
- Started with FastAPI for async scalability and modular architecture
- PostgreSQL chosen for robustness and SQL features
- Redis and Celery added for performance, background tasks
- GitHub used for collaboration, version control, and long-term project record

## Roadmap Progress
- [x] Phase 1: Core Setup (project scaffold, DB config)
- [ ] Phase 2: User Management (auth, roles, tenants)
- [ ] Phase 3: First Module (CRM: Leads, Contacts, Pipeline)
- [ ] Phase 4: Dockerize + Setup CI/CD
- [ ] Phase 5: AI Feature Prototype (e.g., PO generation)

## 🗓️ July 30, 2025 – Project Setup and Architecture Decisions

- ✅ Chose FastAPI (Python) for its async performance, scalability, and clean API design.
- ✅ PostgreSQL selected as the primary RDBMS for reliability and JSONB support.
- ✅ Redis + Celery included for background tasks and real-time features.
- ✅ Docker + `.env` setup created for isolated, replicable environments.
- ✅ Project initialized with the following structure:

erp-app/
├── app/
│ ├── api/ # API routers by module (users, inventory, etc.)
│ ├── core/ # Configs (DB, settings, security)
│ ├── models/ # SQLAlchemy models
│ ├── schemas/ # Pydantic models (for request/response)
│ ├── services/ # Business logic
│ ├── db/ # Database session, init, seeders
│ └── main.py # Entry point
├── alembic/ # DB migrations
├── .env # Environment variables
├── Dockerfile # Container build
├── docker-compose.yml # Compose for PostgreSQL, Redis, etc.
└── README.md

- ✅ Included Jinja2 support for early admin panel interface and Swagger UI for API testing.

---

## 🗓️ July 31, 2025 – Authentication and Role Strategy Finalized

- ✅ Chose `passlib` + `bcrypt` for secure password hashing with future upgradeability.
- ✅ Defined initial `User`, `Role`, and `Permission` model relationships.
- ✅ Chose JWT as the authentication strategy with endpoints:
  - `/register`
  - `/login`
  - `/me`
- ✅ Designed for multi-tenant structure (users assigned to organizations).
- ✅ Role system supports:
  - Default roles (`admin`, `sales_rep`, `manager`)
  - Custom role creation per tenant
  - Flexible permission linking (`view_crm`, `edit_invoice`, etc.)
- ✅ Route-level protection planned via permission decorators like:
  ```python
  @requires_permission("edit_crm")
