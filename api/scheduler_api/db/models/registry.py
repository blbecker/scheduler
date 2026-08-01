"""
Central import point for SQLModel/Alembic.

Importing this module guarantees all tables are registered
in SQLModel.metadata.
"""

# ─────────────────────────────
# CORE
# ─────────────────────────────
from scheduler_api.db.models.core.skill import SkillModel
from scheduler_api.db.models.core.worker import WorkerModel

# ─────────────────────────────
# ASSIGNMENTS
# ─────────────────────────────
from scheduler_api.db.models.assignments.shift_assignment import ShiftAssignmentModel

# ─────────────────────────────
# ASSOCIATIONS (must load before relationships resolve)
# ─────────────────────────────
from scheduler_api.db.models.associations.worker_skill_link import WorkerSkillLinkModel
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLinkModel
from scheduler_api.db.models.associations.shift_template_skill import (
    ShiftTemplateSkillModel,
)

# ─────────────────────────────
# TEMPLATES
# ─────────────────────────────
from scheduler_api.db.models.templates.schedule_template import ScheduleTemplateModel
from scheduler_api.db.models.templates.shift_template import ShiftTemplateModel

# ─────────────────────────────
# SCHEDULES (OUTPUT)
# ─────────────────────────────
from scheduler_api.db.models.schedules.schedule import ScheduleModel
from scheduler_api.db.models.schedules.shift import ShiftModel

# ─────────────────────────────
# SOLVES / ORCHESTRATION
# ─────────────────────────────
from scheduler_api.db.models.solves.schedule_solve import ScheduleSolveModel

# Optional convenience export (not required for Alembic)
__all__ = [
    # core
    "SkillModel",
    "WorkerModel",
    # assignments
    "ShiftAssignmentModel",
    # associations
    "WorkerSkillLinkModel",
    "ShiftSkillLinkModel",
    "ShiftTemplateSkillModel",
    # templates
    "ScheduleTemplateModel",
    "ShiftTemplateModel",
    # schedules (output)
    "ScheduleModel",
    "ShiftModel",
    # solves / orchestration
    "ScheduleSolveModel",
]
