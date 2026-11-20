from pydantic import BaseModel, ConfigDict


class EngineModel(BaseModel):
    """Common frozen base for every engine boundary DTO."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
    )
