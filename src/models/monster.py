from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.drop import Drop
    from src.models.sub_area import SubArea

monster_sub_area_association = Table(
    "monster_sub_area_association",
    Base.metadata,
    Column("sub_area_id", ForeignKey("sub_area.id")),
    Column("monster_id", ForeignKey("monster.id")),
)


class Monster(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False)
    earth_resistance: Mapped[int] = mapped_column(nullable=False)
    air_resistance: Mapped[int] = mapped_column(nullable=False)
    fire_resistance: Mapped[int] = mapped_column(nullable=False)
    water_resistance: Mapped[int] = mapped_column(nullable=False)
    sub_areas: Mapped[List["SubArea"]] = relationship(
        secondary=monster_sub_area_association, back_populates="monsters"
    )
    drops: Mapped[List["Drop"]] = relationship(back_populates="monster")

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return self.__str__()
