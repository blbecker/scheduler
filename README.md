# scheduler

## UI

### Generate API client

`pushd ui/scheduler_ui && orval && popd`

## Database

### Running migrations (local dev)

`docker compose run api alembic upgrade head`

### Creating migrations

`docker compose run api alembic revision --autogenerate -m "<message>"`
