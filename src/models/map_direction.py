from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from EzreD2Shared.shared.enums import FromDirection, ToDirection
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.map import Map


class MapDirection(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    from_map_id: Mapped[int] = mapped_column(ForeignKey("map.id"), nullable=False)
    from_map: Mapped["Map"] = relationship(
        back_populates="map_directions", foreign_keys=[from_map_id]
    )
    from_direction: Mapped[FromDirection] = mapped_column(nullable=False)

    to_map_id: Mapped[int] = mapped_column(ForeignKey("map.id"))
    to_map: Mapped["Map"] = relationship(foreign_keys=[to_map_id])
    to_direction: Mapped[ToDirection] = mapped_column(nullable=False)
    was_checked: Mapped[bool] = mapped_column(default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "from_map_id",
            "from_direction",
            "to_map_id",
            "to_direction",
            name="unique direction",
        ),
    )

    def __str__(self) -> str:
        return f"{self.from_direction}:{self.from_map} -> {self.to_direction} -> {self.to_map}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, MapDirection)
            and self.from_direction == value.from_direction
            and self.from_map_id == value.from_map_id
            and self.to_direction == value.to_direction
            and self.to_map_id == value.to_map_id
        )

    def __hash__(self) -> int:
        return (
            self.from_direction,
            self.from_map_id,
            self.to_direction,
            self.to_map_id,
        ).__hash__()
