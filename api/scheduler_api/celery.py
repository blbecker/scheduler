import os
from celery import Celery


app = Celery("scheduler_api")
app.autodiscover_tasks()
