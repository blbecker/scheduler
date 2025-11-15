import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from scheduler_api.models.template import ScheduleTemplate
from scheduler_api.models.template import ShiftTemplate


@pytest.fixture
def simple_shift_template():
    return ShiftTemplate(
        id=uuid4(),
        start_time=datetime(2024, 1, 1, 9, 0),
        end_time=datetime(2024, 1, 1, 17, 0),
        required_skills=[],
    )


@pytest.fixture
def simple_schedule_template(simple_shift_template):
    return ScheduleTemplate(
        id=uuid4(),
        start_time=datetime(2024, 1, 1),
        end_time=datetime(2024, 1, 2),
        shifts=[simple_shift_template],
    )
