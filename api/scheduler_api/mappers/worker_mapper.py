from scheduler_api.models import Worker
from scheduler_api.schemas.worker import WorkerRead
from typing import List
import logging

logger = logging.getLogger(__name__)


def worker_to_read(worker: Worker) -> WorkerRead:
    return WorkerRead(
        id=worker.id,
        name=worker.name,
        email=worker.email,
        phone=worker.phone,
        birthdate=worker.birthdate,
        hourly_rate=0,
        skills=[s.id for s in worker.skills],
    )


def list_workers_to_read(workers: List[Worker]) -> List[WorkerRead]:
    return [worker_to_read(w) for w in workers]
