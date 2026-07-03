from fastapi import FastAPI, APIRouter
from .db import init_db
from .routers import (
    shifts,
    skills,
    workers,
    scheduler,
    schedule_templates,
    shift_templates,
    schedules,
    schedule_generation_runs,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Scheduler API")
v1router = APIRouter()

origins = [
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


v1router.include_router(skills.router)
v1router.include_router(shifts.router)
v1router.include_router(workers.router)
v1router.include_router(scheduler.router)
v1router.include_router(schedule_templates.router)
v1router.include_router(shift_templates.router)
v1router.include_router(schedules.router)
v1router.include_router(schedule_generation_runs.router)
app.include_router(v1router, prefix="/v1")
