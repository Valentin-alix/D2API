from datetime import time
from sqlalchemy.orm import Session

from src.models.user import ConfigUser, RangeHourPlayTime, RangeTime
from src.queries.utils import get_or_create


DEFAULT_RANGES_HOURS_PLAYTIME: list[tuple[time, time]] = [
    (time(hour=8), time(hour=12, minute=30)),
    (time(hour=13), time(hour=20, minute=30)),
    (time(hour=21), time(hour=23, minute=45)),
]


def populate_config(session: Session, user_id: int):
    """used at user creation"""
    range_wait = get_or_create(
        session,
        RangeTime,
        start_time=time(microsecond=300000),
        end_time=time(microsecond=700000),
        commit=False,
    )[0]
    range_new_map = get_or_create(
        session,
        RangeTime,
        start_time=time(second=1),
        end_time=time(second=6),
        commit=False,
    )[0]
    session.add(
        ConfigUser(range_wait=range_wait, range_new_map=range_new_map, user_id=user_id)
    )

    range_hours: list[RangeHourPlayTime] = []
    for range_hour in DEFAULT_RANGES_HOURS_PLAYTIME:
        range_hours.append(
            RangeHourPlayTime(
                start_time=range_hour[0], end_time=range_hour[1], config_user_id=1
            )
        )
    session.add_all(range_hours)
    session.commit()
