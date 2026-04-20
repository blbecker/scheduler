from fastapi import FastAPI, APIRouter

# from .db import init_db
from .routers import (
    shifts,
    skills,
    workers,
    schedule_generation_jobs,
    schedule_templates,
)
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(title="Scheduler API")
v1router = APIRouter()

logging.basicConfig(
    level=logging.DEBUG,  # Show debug logs
    format="%(asctime)s [%(levelname)s] %(message)s",
)

origins = [
    "http://localhost:9000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# def on_startup():
#     init_db()


v1router.include_router(skills.router)
v1router.include_router(shifts.router)
v1router.include_router(workers.router)
v1router.include_router(schedule_generation_jobs.router)
v1router.include_router(schedule_templates.router)
app.include_router(v1router, prefix="/v1")
