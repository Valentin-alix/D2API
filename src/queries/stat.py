from cachetools import cached
from sqlalchemy.orm import Session, selectinload

from src.models.rune import Stat


@cached(cache={})
def get_stats_query(session: Session) -> list[Stat]:
    return session.query(Stat).options(selectinload(Stat.runes)).all()
