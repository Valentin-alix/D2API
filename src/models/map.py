from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ColumnElement, ForeignKey, case, func
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.sub_area import SubArea

if TYPE_CHECKING:
    from src.models.collectable import CollectableMapInfo
    from src.models.waypoint import Waypoint
from src.models.world import World


class Map(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(nullable=False)

    world_id: Mapped[int] = mapped_column(ForeignKey("world.id"), nullable=False)
    world: Mapped[World] = relationship()

    sub_area_id: Mapped[int] = mapped_column(ForeignKey("sub_area.id"), nullable=False)
    sub_area: Mapped["SubArea"] = relationship(back_populates="maps")

    # neighbors
    left_map_id: Mapped[int | None] = mapped_column(ForeignKey("map.id"), nullable=True)
    left_map_was_checked: Mapped[bool] = mapped_column(nullable=False, default=False)
    left_map: Mapped[Map | None] = relationship(foreign_keys=[left_map_id])

    right_map_id: Mapped[int | None] = mapped_column(
        ForeignKey("map.id"), nullable=True
    )
    right_map_was_checked: Mapped[bool] = mapped_column(nullable=False, default=False)
    right_map: Mapped[Map | None] = relationship(foreign_keys=[right_map_id])

    top_map_id: Mapped[int | None] = mapped_column(ForeignKey("map.id"), nullable=True)
    top_map_was_checked: Mapped[bool] = mapped_column(nullable=False, default=False)
    top_map: Mapped[Map | None] = relationship(foreign_keys=[top_map_id])

    bot_map_id: Mapped[int | None] = mapped_column(ForeignKey("map.id"), nullable=True)
    bot_map_was_checked: Mapped[bool] = mapped_column(nullable=False, default=False)
    bot_map: Mapped[Map | None] = relationship(foreign_keys=[bot_map_id])

    waypoint: Mapped["Waypoint | None"] = relationship(
        back_populates="map", uselist=False
    )
    collectables_map_info: Mapped[List["CollectableMapInfo"]] = relationship(
        back_populates="map"
    )

    can_havre_sac: Mapped[bool] = mapped_column(nullable=False, default=True)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Map) and value.id == self.id

    def __hash__(self) -> int:
        return self.id.__hash__()

    def __str__(self) -> str:
        return f"id: {self.id} pos: {self.x}:{self.y} {self.world.name}"

    def __repr__(self) -> str:
        return self.__str__()

    @hybrid_method
    def get_dist_map(self, map: "Map") -> float:  # type: ignore
        # Manhattan distance
        if self.world_id != map.world_id:
            return float("inf")
        return abs(self.x - map.x) + abs(self.y - map.y)

    @get_dist_map.expression  # type: ignore
    @classmethod
    def get_dist_map(cls, map: "Map") -> ColumnElement[int]:
        return case(
            (
                cls.world_id == map.world_id,
                func.abs(cls.x - map.x) + func.abs(cls.y - map.y),
            ),
            else_=float("inf"),
        )
