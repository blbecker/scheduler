"""
Central import point for SQLModel/Alembic.

Importing this module guarantees all tables are registered
in SQLModel.metadata.
"""

# ─────────────────────────────
# CORE
# ─────────────────────────────
from scheduler_api.db.models.core.skill import Skill
from scheduler_api.db.models.core.worker import Worker

# ─────────────────────────────
# ASSOCIATIONS (must load before relationships resolve)
# ─────────────────────────────
from scheduler_api.db.models.associations.worker_skill_link import WorkerSkillLink
from scheduler_api.db.models.associations.shift_worker_link import ShiftWorkerLink
from scheduler_api.db.models.associations.shift_skill_link import ShiftSkillLink
from scheduler_api.db.models.associations.shift_template_skill import ShiftTemplateSkill

# ─────────────────────────────
# TEMPLATES
# ─────────────────────────────
from scheduler_api.db.models.templates.schedule_template import ScheduleTemplate
from scheduler_api.db.models.templates.shift_template import ShiftTemplate

# ─────────────────────────────
# SCHEDULES (OUTPUT)
# ─────────────────────────────
from scheduler_api.db.models.schedules.schedule import Schedule
from scheduler_api.db.models.schedules.shift import Shift

# ─────────────────────────────
# RUNS / ORCHESTRATION
# ─────────────────────────────
from scheduler_api.db.models.runs.schedule_generation_run import ScheduleGenerationRun

# Optional convenience export (not required for Alembic)
__all__ = [
    # core
    "Skill",
    "Worker",
    # associations
    "WorkerSkill",
    "ShiftWorkerLink",
    "ShiftSkillLink",
    "ShiftTemplateSkill",
    # templates
    "ScheduleTemplate",
    "ShiftTemplate",
    # schedules
    "Schedule",
    "Shift",
    # runs
    "ScheduleGenerationRun",
]
