from typing import TYPE_CHECKING, Any, List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from D2Shared.shared.consts.areas import AGRESSIVE_LIMIT, FARMABLE_SUB_AREAS
from src.models.base import Base
from src.models.monster import Monster, monster_sub_area_association
from src.models.area import Area

if TYPE_CHECKING:
    from src.models.map import Map
    from src.models.world import World


class SubArea(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False)
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    area: Mapped[Area] = relationship()
    maps: Mapped[List["Map"]] = relationship(back_populates="sub_area")
    level: Mapped[int] = mapped_column(nullable=False)
    monsters: Mapped[List[Monster]] = relationship(
        secondary=monster_sub_area_association, back_populates="sub_areas"
    )

    __table_args__ = (
        UniqueConstraint("name", "area_id", name="unique sub area in area"),
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, SubArea) and value.id == self.id

    def __hash__(self) -> int:
        return self.id.__hash__()

    @hybrid_property
    def is_farmable(self) -> bool:  # type: ignore
        return self.id in FARMABLE_SUB_AREAS

    @is_farmable.expression
    def is_farmable(cls):
        return cls.id.in_(FARMABLE_SUB_AREAS)  # type: ignore

    @hybrid_method
    def is_not_aggressive(self, character_lvl: int) -> bool:
        return self.level <= AGRESSIVE_LIMIT + character_lvl

    @property
    def world(self) -> "World":
        return self.maps[0].world
