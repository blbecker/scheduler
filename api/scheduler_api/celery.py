from celery import Celery
import os

app = Celery(
    "scheduler_api",
    broker=os.getenv(
        "CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//"
    ),  # <-- container hostname
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

# Auto-discover all tasks in the scheduler_api package
app.autodiscover_tasks(packages=["scheduler_api"])
