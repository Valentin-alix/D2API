from __future__ import annotations
from datetime import datetime, time

from sqlalchemy import CheckConstraint, Column, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class RangeHourPlayTime(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    config_user_id: Mapped[int] = mapped_column(
        ForeignKey("config_user.id", ondelete="CASCADE"), nullable=False
    )
    config_user: Mapped[ConfigUser] = relationship(
        back_populates="ranges_hour_playtime"
    )

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time", name="check_end_time_greater_than_start_time"
        ),
    )


class RangeWait(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    start: Mapped[float] = mapped_column(nullable=False)
    end: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint('"end" > start', name="check_end_greater_than_start"),
        CheckConstraint("start >= 0", name="positive start"),
    )


class ConfigUser(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    ranges_hour_playtime: Mapped[list[RangeHourPlayTime]] = relationship(
        back_populates="config_user"
    )
    afk_time_at_start = Column(Time, default=time())
    time_between_sentence = Column(Time, default=time(minute=30))
    time_fighter = Column(Time, default=time(hour=1))
    time_harvester = Column(Time, default=time(hour=4))
    randomizer_duration_activity: Mapped[float] = mapped_column(
        default=0.4, nullable=False
    )

    range_new_map_id: Mapped[int] = mapped_column(
        ForeignKey("range_wait.id"), nullable=False
    )
    range_new_map: Mapped[RangeWait] = relationship(foreign_keys=[range_new_map_id])

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "randomizer_duration_activity >= 0 and randomizer_duration_activity <= 1",
            name="coherent randomizer_duration_activity",
        ),
    )


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    sub_expire: Mapped[datetime] = mapped_column(default=datetime(2100, 1, 1))
    config_user: Mapped[ConfigUser] = relationship()

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.id.__hash__()
