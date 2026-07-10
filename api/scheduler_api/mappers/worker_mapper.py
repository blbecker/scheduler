# scheduler_api/mappers/worker_mapper.py
from scheduler_api.db.models.core.worker import WorkerModel
from scheduler_api.schemas.worker import WorkerCreate, WorkerResponse, WorkerUpdate


def to_response(model: WorkerModel) -> WorkerResponse:
    return WorkerResponse(
        id=model.id,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def from_create(dto: WorkerCreate) -> WorkerModel:
    return WorkerModel(**dto.model_dump())


def apply_update(model: WorkerModel, dto: WorkerUpdate) -> WorkerModel:
    data = dto.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(model, k, v)
    return model
