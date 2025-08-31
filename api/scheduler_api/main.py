from fastapi import FastAPI, APIRouter
from .db import init_db
from .routers import shifts, skills, workers

app = FastAPI(title="Scheduler API")
v1router = APIRouter()


@app.on_event("startup")
def on_startup():
    init_db()


v1router.include_router(skills.router, prefix="/skills", tags=["skills"])
v1router.include_router(shifts.router, prefix="/shifts", tags=["shifts"])
v1router.include_router(workers.router, prefix="/workers", tags=["workers"])
app.include_router(v1router, prefix="/v1")
