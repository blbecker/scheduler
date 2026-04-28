from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID, uuid4


@dataclass
class ScheduleLayout:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    date_range_start: datetime = field(default_factory=datetime.utcnow)
    date_range_end: datetime = field(default_factory=datetime.utcnow)
    shift_templates: List[Dict[str, Any]] = field(default_factory=list)
    worker_ids: List[UUID] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)