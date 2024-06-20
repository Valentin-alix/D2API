from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.navigations.map import Map


class Waypoint(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    map_id: Mapped[int] = mapped_column(
        ForeignKey("map.id"), nullable=False, unique=True
    )
    map: Mapped["Map"] = relationship(back_populates="waypoint")

    def __hash__(self) -> int:
        return self.map.__hash__()

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Waypoint) and self.map == value.map

    def __str__(self) -> str:
        return str(self.map)

    def __repr__(self) -> str:
        return self.__str__()
