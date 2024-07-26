from __future__ import annotations

from typing import List

from sqlalchemy import CheckConstraint, Column, ForeignKey, Table
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from D2Shared.shared.consts.jobs import HARVEST_JOBS_NAME
from D2Shared.shared.enums import ElemEnum
from src.models.base import Base
from src.models.item import Item
from src.models.job import Job
from src.models.recipe import Recipe
from src.models.server import Server
from src.models.spell import Spell
from src.models.sub_area import SubArea
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

character_sub_areas_association = Table(
    "character_sub_areas_association",
    Base.metadata,
    Column("character_id", ForeignKey("character.id", ondelete="CASCADE")),
    Column("sub_area_id", ForeignKey("sub_area.id")),
)

character_recipe_association = Table(
    "character_recipe_association",
    Base.metadata,
    Column("character_id", ForeignKey("character.id", ondelete="CASCADE")),
    Column("recipe_id", ForeignKey("recipe.id")),
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
    sub_areas: Mapped[List["SubArea"]] = relationship(
        secondary=character_sub_areas_association
    )
    recipes: Mapped[List["Recipe"]] = relationship(
        secondary=character_recipe_association
    )
    po_bonus: Mapped[int] = mapped_column(nullable=False, default=0)
    elem: Mapped[ElemEnum] = mapped_column(default=ElemEnum.ELEMENT_WATER)
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"), nullable=False)
    server: Mapped[Server] = relationship()

    bank_items: Mapped[List["Item"]] = relationship(
        secondary=character_items_association
    )
    spells: Mapped[List["Spell"]] = relationship(cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("lvl>=1 AND lvl<=200", name="check legit character lvl"),
        CheckConstraint("po_bonus>=0", name="check positive po bonus"),
    )

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def max_pods(self):
        BASE_PODS = 1000

        sum_job_lvls = sum((elem.lvl for elem in self.character_job_info))
        bonus_pods = 0
        pod_by_lvl = 12
        for _ in range(200, sum_job_lvls, 200):
            bonus_pods += 200 * pod_by_lvl
            pod_by_lvl = max(pod_by_lvl - 1, 1)
        bonus_pods += (sum_job_lvls % 200) * pod_by_lvl

        return BASE_PODS + self.lvl * 5 + bonus_pods

    @property
    def harvest_jobs_infos(self) -> list[CharacterJobInfo]:
        return [
            job_info
            for job_info in self.character_job_info
            if job_info.job.name in HARVEST_JOBS_NAME
        ]
