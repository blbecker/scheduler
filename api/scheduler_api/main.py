from fastapi import FastAPI
from .db import init_db
from .routers import shifts, skills, workers

app = FastAPI(title="Scheduler API")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(shifts.router, prefix="/shifts", tags=["skills"])
app.include_router(workers.router, prefix="/workers", tags=["skills"])
