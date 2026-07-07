from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class ScheduleLayout:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: Optional[str] = None
    date_range_start: datetime = field(default_factory=datetime.utcnow)
    date_range_end: datetime = field(default_factory=datetime.utcnow)
    shift_templates: list[dict[str, Any]] = field(default_factory=list)
    worker_ids: list[UUID] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
