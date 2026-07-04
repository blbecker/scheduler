# scheduler

## Database

### Running migrations (local dev)

`docker compose run api alembic upgrade head`

### Creating migrations

`docker compose run api alembic revision --autogenerate -m "<message>"`
