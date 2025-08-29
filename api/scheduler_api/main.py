from fastapi import FastAPI, APIRouter, Depends
from .db import init_db
from .routers import shifts, skills, workers

app = FastAPI(title="Scheduler API")
v1router = APIRouter()


@app.on_event("startup")
def on_startup():
    init_db()


v1router.include_router(skills.router, prefix="/v1", tags=["v1"])
v1router.include_router(shifts.router, prefix="/shifts", tags=["skills"])
v1router.include_router(workers.router, prefix="/workers", tags=["skills"])
app.include_router(v1router, prefix="/v1")
