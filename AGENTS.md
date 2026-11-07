# AGENTS.md

Workforce shift scheduling. API: FastAPI + SQLModel + Celery, Postgres, RabbitMQ/Redis.
UI: Vue 3 + Quasar. Licensed AGPL-3.0 — this repository is public.

## Where requirements live

**Not in this repository.** Product, domain, and architecture specs live in the
private OpenSpec store `scheduler-specs`. This repo's `openspec/config.yaml` points
at it:

```yaml
store: scheduler-specs
```

Before implementing anything, read the requirements:

```bash
openspec list --specs                    # capabilities
openspec show <capability> --type spec   # requirements + scenarios
openspec list                            # in-flight changes
```

On a machine without the store registered, these commands fail loudly. Clone
`blbecker/scheduler-specs` and run `openspec store register <path>` — do **not**
guess the intended behavior from the code.

## Rules

- **Behavior is specified in the store, not invented here.** If no requirement
  covers what you are about to build, stop and ask. Do not infer intent from
  existing code — a lot of it is deliberately provisional.
- **Requirements carry IDs** (`REQ-WRK-001`, `REQ-SCHED-002`, …). Reference the ID
  in the commit or PR body, and tag the test that proves it
  (`@pytest.mark.req("REQ-...")`).
- **A requirement marked `provisional` is a first cut, not a bug.** Implement it as
  written. Do not generalize it, harden it, or add options it does not ask for.
- **The API surface is not the spec.** Route shapes follow from the implementable
  requirements; do not add endpoints "for completeness".
- Do not copy spec text into this repo. Link to it.

## Loop

```
propose (store)  →  apply (here)  →  archive (store)
```

Changes are opened and archived in `scheduler-specs`. This repo only ever carries the
implementation of an already-agreed change, and `openspec` skills under
`.hermes/skills/` are installed for that workflow.

## Local development

```bash
docker compose up --build          # api, worker, ui, db, rabbitmq, redis
```

## Checks (CI runs all of these)

```bash
# API
cd api && black --check . && flake8 . && pytest

# UI
cd ui/scheduler_ui && pnpm install && pnpm run lint && pnpm run test:unit:ci
```

Dependencies are managed by Renovate for the API and UI; do not bump versions by
hand unless fixing a security issue.

## Conventions

- Layer per resource: `routers/` → `services/` → `repositories/` → `db/models/`,
  with `schemas/` (Pydantic) and `mappers/` at the boundary. Keep new code in the
  same shape.
- Migrations are Alembic (`api/scheduler_api/db/migrations/`); every model change
  ships one.
- Async work belongs in a Celery task, invoked through the service layer, never
  from a route directly.
