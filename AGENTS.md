# AGENTS.md - Scheduler Project Guide

## Architecture Overview
- **Monorepo**: `/api` (Python FastAPI backend) and `/ui` (Quasar Vue frontend) as separate services
- **Core feature**: Extensible solve framework for schedule optimization (`api/scheduler_api/solves/`)
- **Async processing**: Celery tasks with RabbitMQ broker and Redis result backend
- **Database**: PostgreSQL with SQLAlchemy/SQLModel ORM, migrations already configured and working

## API Design Rules
### Request/Response DTOs (Domain-Oriented)
- **Canonical schema naming**: Use domain entity names for creation schemas (e.g., `Worker` not `WorkerCreate`)
- **Update schemas**: Keep `{Resource}Update` suffix for PATCH/PUT operations  
- **Response schemas**: Keep `{Resource}Response` for GET responses
- **Solve framework**: Use `ScheduleSolveRequest`, `ScheduleSolveCreateResponse`, `ScheduleSolveStatus`, `ScheduleSolveResult`
- **Example**: `/v1/solves/schedule` uses `ScheduleSolveRequest` and `ScheduleSolveCreateResponse`

### URL Pattern Rules
- **POST endpoints go to collection base path** (e.g., `/v1/solves/schedule`), not to specific IDs
- **Resource IDs belong in request body** for creation, not URL path
- **Example**: `POST /v1/solves/schedule` with `template_id` in request body, not `POST /v1/solves/schedule/{template_id}`
- **GET/PUT/DELETE for specific resources** use ID in path (e.g., `/v1/solves/schedule/{solve_id}`)

### Route Organization
- **Hierarchical directory structure**: Routes organized by domain under `/api/scheduler_api/api/v1/routes/`
  - `core/` - Core resources (workers, skills, shifts)
  - `templates/` - Template resources (shift-templates, schedule-templates)
  - `schedules/` - Schedule resources
  - `solves/` - Solve framework resources
- **Flat URL paths**: Routes use flat paths (e.g., `/workers`, `/skills`) not hierarchical URLs
- **Clean imports**: Router organization is for code structure only, not URL paths

### API Documentation & Client Generation
- **Hierarchical tags**: Use domain-specific tags (e.g., `["workers"]`, `["shift-templates"]`, `["schedule-solves"]`)
- **Operation IDs**: All endpoints must have unique `operation_id` for clean client code generation
  - CRUD patterns: `list_{resources}`, `get_{resource}`, `create_{resource}`, `update_{resource}`, `delete_{resource}`
  - Solve patterns: `create_schedule_solve`, `get_schedule_solve_status`, `get_schedule_solve_result`

## Development Commands
### Full stack development
```bash
docker-compose up  # Starts all services: API (8000), UI (9000), worker, RabbitMQ, Redis, PostgreSQL
```

### API (Python backend)
```bash
cd api
pip install -r requirements.txt
uvicorn scheduler_api.main:app --reload  # Dev server (port 8000)
pytest --cov --cov-fail-under 90        # Tests with 90% coverage requirement
black --check .                         # Formatting check
flake8 .                                # Linting (max line length:84)
```

### UI (Quasar Vue frontend)
```bash
cd ui/scheduler_ui
pnpm install                           # Uses pnpm (not npm/yarn as README suggests)
pnpm quasar dev                        # Dev server (port 9000)
pnpm run test:unit:ci                  # CI tests
pnpm run test:unit:ui                  # Interactive test UI
pnpm run lint                          # ESLint
pnpm run format                        # Prettier formatting
pnpm run build                         # Production build
```

## CI/CD Pipeline Notes
- **GitHub Actions**: Enforces 90% test coverage for API (strict)
- **Parallel jobs**: Lint and test run separately for API and UI
- **Build triggers**: Docker images built on push/release only, not on PRs
- **Image registry**: GitHub Container Registry with semantic version tags
- **Renovate**: Uses shared config from `blbecker/renovate-config`

## Testing Strategy
### API testing
- `pytest` with 90% coverage enforcement (CI will fail below threshold)
- Mock-based unit tests (`pytest-mock`) - tests mock external dependencies
- Integration tests use `conftest.py` fixtures
- No test database required - tests mock database interactions

### UI testing
- `vitest` with Vue Test Utils
- `msw` (Mock Service Worker) for API mocking
- Component tests in `test/vitest/__tests__/`

## Environment & Ports
### Required services (docker-compose)
- **API**: port 8000 (FastAPI)
- **UI**: port 9000 (Quasar dev server)
- **Worker**: Celery worker processing tasks
- **RabbitMQ**: 5672 (AMQP), 15672 (management UI)
- **Redis**: 6379 (result backend)
- **PostgreSQL**: 5432 (database)

### Environment variables (already in docker-compose.yml)
```bash
PG_USER=scheduler_user
PG_PASS=scheduler_pass
PG_HOST=db (docker service name)
PG_PORT=5432
PG_DB=scheduler_db
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Gotchas & Important Details
1. **Package manager**: UI uses `pnpm` despite README mentioning yarn/npm (check `pnpm-lock.yaml`)
2. **Database migrations**: Already configured with alembic and working migrations
3. **Solve framework**: Extensible genetic algorithm framework in `solves/` directory
4. **Bruno API testing**: Contains `.bru` files in `/bruno/` for manual API validation
5. **Volume mounts**: Development code mounted for hot reload; `node_modules` volume avoids host conflicts
6. **Non-root users**: Docker containers run as `appuser` (UID/GID 1000) for security
7. **Python version**: 3.12 specific (see Dockerfile and CI)
8. **Node version**: Wide range (18-28) in UI package.json engines
9. **Coverage strictness**: 90% minimum enforced in CI - failing tests block builds
10. **Flake8 config**: 180 character line length limit (not standard 79/88)
11. **API DTOs**: All endpoints must use Pydantic models - no raw dict returns

## Project Structure Key Points
### API (`/api/scheduler_api/`)
- `db/` - Database models and configuration with working migrations
- `domain/` - Core business logic (Schedule, Population, ScheduleLayout)
- `solves/` - Extensible solve framework for schedule optimization (replaces old genetic/)
  - `engine/` - Evolution engine, population management, orchestration
  - `interfaces/` - Protocol definitions for extensible components
  - `schedule/` - Schedule-specific implementations (genome, solver, components)
- `routers/` - FastAPI route handlers (shifts, skills, workers, schedules, solves)
- `schemas/` - Pydantic models for request/response validation (REQUIRED for all APIs)
- `services/` - Business logic services
- `tasks/` - Celery background tasks

### UI (`/ui/scheduler_ui/`)
- Quasar framework with TypeScript
- Vue Query (`@tanstack/vue-query`) for API state management
- Client services for API calls (`src/services/`)
- Generated API client models (`src/models/`)
- Quasar-specific build configuration

## Development Workflow
1. **PR workflow**: "Make a PR for your changes" is the current expectation
2. **Testing**: Write unit tests for all changes, mock external dependencies
3. **Documentation**: Keep AGENTS.md and other docs updated with changes
4. **Security**: Maintain clean and secure project practices
5. **docker-compose.yml**: Provides complete working dev environment - no additional env vars needed
6. **API design**: Always define request/response DTOs in schemas/, never return raw dicts

## Workflow Constraints
1. **Test order**: CI runs lint → test (both API and UI)
2. **Build dependencies**: UI build requires API tests to pass
3. **Coverage enforcement**: API tests must maintain 90% coverage (strict)
4. **Docker caching**: Uses GitHub Actions cache for pnpm and Docker layers
5. **Release automation**: Auto-creates GitHub releases with changelog on push to main
6. **API consistency**: All endpoints must follow DTO pattern - violations block PRs