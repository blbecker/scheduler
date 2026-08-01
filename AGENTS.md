# AGENTS.md - Scheduler Project Quick Guide

## Architecture
- Monorepo: `/api` (Python FastAPI) + `/ui` (Next.js React)
- Async processing: Celery + RabbitMQ + Redis
- Database: PostgreSQL with SQLAlchemy/SQLModel
- Core: Extensible solve framework (`solves/`) with genetic algorithm engine

## Quick Start
```bash
docker-compose up  # All services: API (8000), UI (9000), worker, RabbitMQ, Redis, PostgreSQL
```

## Development Commands
### API Backend
```bash
cd api
pip install -r requirements.txt
uvicorn scheduler_api.main:app --reload  # port 8000
pytest --cov --cov-fail-under 90        # 90% coverage required
black --check . && flake8 .              # Formatting + linting (180 char limit)
```

### UI Frontend (Next.js React)
```bash
cd ui/scheduler_ui
pnpm install && pnpm dev                 # port 9000 (uses pnpm, not npm/yarn)
pnpm test                                # Run tests
pnpm lint && pnpm format                 # Linting + formatting (Biome)
```

## Essential Patterns
### API Design
- Services own transactions: explicit `session.flush()` + `session.commit()`
- Repositories: data access only, never commit/rollback
- DTO naming: `{Resource}Create`, `{Resource}Update`, `{Resource}Response`
- POST endpoints: collection path (`/v1/solves/schedule`), IDs in request body

### Error Handling
- Services raise `ValueError` for not found cases
- Routes return appropriate HTTP status codes (404, 400, etc.)
- Log errors with details, return generic messages to clients

## Environment & Ports
| Service     | Port(s)           | Purpose                  |
|-------------|-------------------|--------------------------|
| API         | 8000              | FastAPI backend          |
| UI          | 9000              | Next.js dev server       |
| RabbitMQ    | 5672, 15672       | Celery broker + mgmt UI  |
| Redis       | 6379              | Result backend           |
| PostgreSQL  | 5432              | Database                 |

## Project Structure
### API (`api/scheduler_api/`)
- `db/` - Models, migrations, database config
- `solves/` - Genetic algorithm framework (engine, interfaces, schedule)
- `routers/` - Route handlers (organized by domain)
- `schemas/` - Pydantic models (REQUIRED for all APIs)
- `services/` - Business logic with transaction ownership
- `tasks/` - Celery background tasks

### UI (`ui/scheduler_ui/`)
- Next.js React framework with TypeScript
- Material-UI components and Data Grid
- React Query for API state management
- Client services for API calls

## Quick Reference
- **Test coverage**: 90% minimum enforced (currently met)
- **Package manager**: UI uses `pnpm` (check `pnpm-lock.yaml`)
- **Database migrations**: Alembic configured, working
- **Code review**: Use `full-stack-code-reviewer` agent for changes
- **Solve statuses**: `pending`, `queued`, `running`, `completed`, `failed`, `cancelled`
- **Key model**: `ScheduleSolveModel` tracks solve lifecycle and progress

**For detailed patterns, architectural decisions, and troubleshooting: check project memory**
