from __future__ import annotations

from typing import List

from sqlalchemy import CheckConstraint, Column, ForeignKey, Table
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from D2Shared.shared.consts.jobs import HARVEST_JOBS_ID
from D2Shared.shared.enums import BreedEnum, ElemEnum
from src.models.base import Base
from src.models.breed import Breed
from src.models.item import Item
from src.models.job import Job
from src.models.server import Server
from src.models.waypoint import Waypoint

character_waypoint_association = Table(
    "character_waypoint_association",
    Base.metadata,
    Column("character_id", ForeignKey("character.id", ondelete="CASCADE")),
    Column("waypoint_id", ForeignKey("waypoint.id")),
)

character_items_association = Table(
    "character_items_association",
    Base.metadata,
    Column("character_id", ForeignKey("character.id", ondelete="CASCADE")),
    Column("item_id", ForeignKey("item.id")),
)


class CharacterJobInfo(Base):
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), primary_key=True)
    job: Mapped["Job"] = relationship()

    lvl: Mapped[int] = mapped_column(nullable=False, default=1)
    weight: Mapped[float] = mapped_column(nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("lvl>=1 AND lvl<=200", name="check legit character job lvl"),
    )


class Character(Base):
    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    lvl: Mapped[int] = mapped_column(nullable=False, default=1)
    character_job_info: Mapped[List["CharacterJobInfo"]] = relationship()
    waypoints: Mapped[List["Waypoint"]] = relationship(
        secondary=character_waypoint_association
    )
    po_bonus: Mapped[int] = mapped_column(nullable=False, default=0)
    is_sub: Mapped[bool] = mapped_column(nullable=False, default=False)
    time_spent: Mapped[float] = mapped_column(default=0)
    breed_id: Mapped[int] = mapped_column(
        ForeignKey("breed.id"), nullable=False, default=BreedEnum.ENI
    )
    breed: Mapped[Breed] = relationship()
    elem: Mapped[ElemEnum] = mapped_column(default=ElemEnum.ELEMENT_WATER)
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"), nullable=False)
    server: Mapped[Server] = relationship()

    bank_items: Mapped[List["Item"]] = relationship(
        secondary=character_items_association
    )

    __table_args__ = (
        CheckConstraint("lvl>=1 AND lvl<=200", name="check legit character lvl"),
        CheckConstraint("po_bonus>=0", name="check positive po bonus"),
        CheckConstraint("time_spent>=0", name="check positive time_spent"),
    )

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def harvest_jobs_infos(self) -> list[CharacterJobInfo]:
        return [
            job_info
            for job_info in self.character_job_info
            if job_info.job_id in HARVEST_JOBS_ID
        ]
