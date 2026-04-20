from __future__ import annotations
from pydantic import BaseModel


class ScoreResult(BaseModel):
    score: float = 0.0
    ok: bool = True
    message: str = ""
