from sqlalchemy.orm import Session

from src.models.user import ConfigUser, RangeWait
from src.queries.utils import get_or_create


def populate_config_user(session: Session, user_id: int):
    """used at user creation"""
    range_new_map = get_or_create(
        session,
        RangeWait,
        start=1,
        end=5,
        commit=False,
    )[0]

    config_user = ConfigUser(range_new_map=range_new_map, user_id=user_id)
    session.add(config_user)
    session.commit()
