from datetime import time
from sqlalchemy.orm import Session

from src.models.user import ConfigUser, RangeHourPlayTime, RangeWait
from src.queries.utils import get_or_create


DEFAULT_RANGES_HOURS_PLAYTIME: list[tuple[time, time]] = [
    (time(hour=8), time(hour=23, minute=30))
]


def populate_config_user(session: Session, user_id: int):
    """used at user creation"""
    range_new_map = get_or_create(
        session,
        RangeWait,
        start=1,
        end=7,
        commit=False,
    )[0]

    config_user = ConfigUser(range_new_map=range_new_map, user_id=user_id)
    session.add(config_user)
    session.commit()

    for range_hour in DEFAULT_RANGES_HOURS_PLAYTIME:
        get_or_create(
            session,
            RangeHourPlayTime,
            start_time=range_hour[0],
            end_time=range_hour[1],
            config_user=config_user,
        )
