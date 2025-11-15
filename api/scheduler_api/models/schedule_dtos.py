from pydantic import BaseModel


class GenerateScheduleInput(BaseModel):
    total_seconds_to_wait: int


class GenerateScheduleResult(BaseModel):
    status: str
    seconds_waited: int
