# AGENTS.md - Scheduler Project Guide

## Architecture Overview
- **Monorepo**: `/api` (Python FastAPI backend) and `/ui` (Quasar Vue frontend) as separate services
- **Core feature**: Extensible solve framework for schedule optimization (`api/scheduler_api/solves/`)
- **Async processing**: Celery tasks with RabbitMQ broker and Redis result backend
- **Database**: PostgreSQL with SQLAlchemy/SQLModel ORM, migrations already configured and working
- **Solve persistence**: Complete solve framework with ScheduleSolveModel tracking solve lifecycle and progress

## API Design Rules
### Transaction Management

#### Service-Owned Transactions
- **Write Operations**: Services call `session.flush()` and `session.commit()` explicitly
- **Read Operations**: No transactions needed
- **Error Handling**: 
  - Services raise `ValueError` for resource not found cases
  - Routes convert to appropriate HTTP status codes (404 for not found)
- **No Retry Logic**: Simple error propagation

#### Repository Responsibilities
- **Data Access Only**: Never call `session.commit()` or `session.rollback()`
- **UUID IDs**: Python-generated, no database sequence needed

#### Key Principles
1. Services own transactions for write operations
2. Repositories are data access only  
3. Routes depend on services, not repositories
4. Log errors with full details, return generic messages

### Request/Response DTOs (Domain-Oriented)
- **Create schemas**: Use `{Resource}Create` suffix (e.g., `WorkerCreate` not `Worker`)
- **Update schemas**: Use `{Resource}Update` suffix for PATCH/PUT operations  
- **Response schemas**: Use `{Resource}Response` for GET responses
- **Solve framework**: Use `ScheduleSolveRequest`, `ScheduleSolveCreateResponse`, `ScheduleSolveStatus`, `ScheduleSolveResult`
- **Example**: `/v1/workers` uses `WorkerCreate` (POST), `WorkerUpdate` (PUT), `WorkerResponse` (GET)

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
pytest --cov --cov-fail-under 90        # Tests with 90% coverage requirement (currently met at 90%)
black --check .                         # Formatting check
flake8 .                                # Linting (max line length: 180)
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
- **GitHub Actions**: Enforces 90% test coverage for API (strict, currently met at 90%)
- **Parallel jobs**: Lint and test run separately for API and UI
- **Build triggers**: Docker images built on push/release only, not on PRs
- **Image registry**: GitHub Container Registry with semantic version tags
- **Renovate**: Uses shared config from `blbecker/renovate-config`

## Testing Strategy
### API testing
- `pytest` with 90% coverage enforcement (CI will fail below threshold, currently met)
- Mock-based unit tests (`pytest-mock`) - tests mock external dependencies including database
- All tests are unit tests with comprehensive mocking - no integration test fixtures or test database
- Solve framework components have comprehensive test coverage

### UI testing
- `vitest` with Vue Test Utils
- `msw` (Mock Service Worker) for API mocking
- Component tests in `test/vitest/__tests__/`

## Code Quality & Review

### Automated Code Review with opencode
- **Agent**: `full-stack-code-reviewer` (available in opencode)
- **Trigger**: After each significant code change in both plan and build modes
- **Scope**: All TypeScript/React components and Python/FastAPI endpoints
- **Focus Areas**:
  - Component simplification and reusability
  - API design compliance with project standards
  - Error handling and loading state patterns
  - Type safety and prop validation
  - Code organization and separation of concerns
  - Performance considerations (memoization, effect dependencies)

### Review Workflow
1. **Plan Mode Reviews**: During feature planning, the agent reviews proposed architecture
2. **Build Mode Reviews**: After implementation, the agent verifies implementation quality
3. **Feedback Integration**: Review findings are incorporated before finalizing changes

### Quality Gates
- All components must pass automated code review before PR submission
- Review feedback should address critical issues before moving to testing phase
- Complex components (>150 lines) receive additional scrutiny for simplification opportunities

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

## Solve Framework Architecture
### Solve Lifecycle & Persistence
- **ScheduleSolveModel**: Complete persistence model tracking solve lifecycle (replaces legacy ScheduleGenerationRun)
- **Solve Statuses**: `pending`, `queued`, `running`, `completed`, `failed`, `cancelled`
- **Progress Tracking**: Real-time tracking of current generation, best fitness, and progress percentage
- **Task Orchestration**: Celery tasks orchestrate solve execution with persistence updates
- **Result Storage**: Completed solves link to generated schedules

### Task Orchestration
- **Background Processing**: Celery tasks handle long-running solve operations
- **Progress Updates**: Task session utility updates solve progress at intervals
- **Error Handling**: Failed solves persist error details for debugging
- **Status Transitions**: Automatic status updates throughout solve lifecycle

## Gotchas & Important Details
1. **Package manager**: UI uses `pnpm` despite README mentioning yarn/npm (check `pnpm-lock.yaml`)
2. **Database migrations**: Already configured with alembic and working migrations
3. **Solve framework**: Complete extensible genetic algorithm framework in `solves/` directory (replaces old genetic/)
4. **Bruno API testing**: Contains `.bru` files in `/bruno/` for manual API validation
5. **Volume mounts**: Development code mounted for hot reload; `node_modules` volume avoids host conflicts
6. **Non-root users**: Docker containers run as `appuser` (UID/GID 1000) for security
7. **Python version**: 3.12 specific (see Dockerfile and CI)
8. **Node version**: Wide range (18-28) in UI package.json engines
9. **Coverage strictness**: 90% minimum enforced in CI - currently met at 90% with comprehensive test suite
10. **Flake8 config**: 180 character line length limit (not standard 79/88)
11. **API DTOs**: All endpoints must use Pydantic models - no raw dict returns
12. **Transaction management**: Services use explicit `session.flush()` and `session.commit()` calls
13. **Error handling**: Simple pattern - services raise `ValueError` for not found, routes return HTTP 404

## Project Structure Key Points
### API (`/api/scheduler_api/`)
- `db/` - Database models and configuration with working migrations
- `domain/` - Core business logic (Schedule, Population, ScheduleLayout)
- `solves/` - Complete extensible solve framework for schedule optimization
  - `engine/` - Evolution engine, population management, orchestration
  - `interfaces/` - Protocol definitions for extensible components
  - `schedule/` - Schedule-specific implementations (genome, solver, constraints, mutators, scorers)
- `routers/` - FastAPI route handlers (shifts, skills, workers, schedules, solves)
- `schemas/` - Pydantic models for request/response validation (REQUIRED for all APIs)
- `services/` - Business logic services with transaction ownership
- `tasks/` - Celery background tasks with solve orchestration

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

## Code Quality Best Practices
### Type Hints with SQLModel
- Use forward references (`"ModelName"`) for type hints with SQLModel circular dependencies
- Import SQLModel classes inside functions when needed to avoid circular imports
- Maintain consistent type hinting throughout the codebase

### Transaction Management
- Services own transaction boundaries with explicit `session.flush()` and `session.commit()`
- Repositories are data access only - never commit or rollback
- Keep transaction logic in service layer only

### Mock-Based Testing
- Mock all external dependencies (database, external services)
- Use `unittest.mock` for comprehensive test isolation
- Test service layer with mocked repositories and sessions
- Solve framework components tested with mock objects

### Import Organization
- Group imports: standard library, third-party, local modules
- Avoid circular imports with careful module organization
- Use absolute imports within the project

## Workflow Constraints
1. **Test order**: CI runs lint → test (both API and UI)
2. **Build dependencies**: UI build requires API tests to pass
3. **Coverage enforcement**: API tests must maintain 90% coverage (strict, currently met)
4. **Docker caching**: Uses GitHub Actions cache for pnpm and Docker layers
5. **Release automation**: Auto-creates GitHub releases with changelog on push to main
6. **API consistency**: All endpoints must follow DTO pattern - violations block PRs