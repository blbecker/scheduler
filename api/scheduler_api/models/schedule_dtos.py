from pydantic import BaseModel, Field


class GenerateScheduleInput(BaseModel):
    total_seconds_to_wait: int = Field(gt=0, le=3600)


class GenerateScheduleResult(BaseModel):
    status: str
    seconds_waited: int
