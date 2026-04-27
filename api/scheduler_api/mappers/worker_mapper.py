# scheduler_api/mappers/worker_mapper.py
from scheduler_api.db.models import Worker
from scheduler_api.schemas.worker import WorkerCreate, WorkerResponse, WorkerUpdate


def to_response(model: Worker) -> WorkerResponse:
    return WorkerResponse(
        id=model.id,
        name=model.name,
        birthdate=model.birthdate,
        email=model.email,
        phone=model.phone,
    )


def from_create(dto: WorkerCreate) -> Worker:
    return Worker(**dto.model_dump())


def apply_update(model: Worker, dto: WorkerUpdate) -> Worker:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model