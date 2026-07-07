# app/api/v1/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scheduler_api.api.v1.routes.core import workers, skills, shifts
from scheduler_api.api.v1.routes.templates import schedule_templates, shift_templates
from scheduler_api.api.v1.routes.schedules import schedules
from scheduler_api.api.v1.routes.solves import schedule


def create_v1_api() -> FastAPI:
    app = FastAPI(
        title="Scheduler API",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url=None)

    app.include_router(skills.router)
    app.include_router(shifts.router)
    app.include_router(workers.router)
    app.include_router(schedule_templates.router)
    app.include_router(shift_templates.router)
    app.include_router(schedules.router)
    app.include_router(schedule.router)

    return app
