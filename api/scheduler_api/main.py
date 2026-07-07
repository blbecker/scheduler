from fastapi import FastAPI, APIRouter
from scheduler_api.db import init_db
from fastapi.middleware.cors import CORSMiddleware
from scheduler_api.api.v1 import create_v1_api

app = FastAPI(title="Scheduler API")
v1_app = create_v1_api()

origins = [
    "http://localhost:3000",
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


app.mount("/api/v1", v1_app)
