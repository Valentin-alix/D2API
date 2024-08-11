from typing import TYPE_CHECKING

from D2Shared.shared.enums import Direction
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.map import Map


from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class MapDirection(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    from_map_id: Mapped[int] = mapped_column(ForeignKey("map.id"), nullable=False)
    from_map: Mapped["Map"] = relationship(
        foreign_keys=[from_map_id], back_populates="map_directions"
    )

    to_map_id: Mapped[int] = mapped_column(ForeignKey("map.id"), nullable=False)
    to_map: Mapped["Map"] = relationship(foreign_keys=[to_map_id])

    was_checked: Mapped[bool] = mapped_column(nullable=False, default=False)
    direction: Mapped[Direction] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("from_map_id", "direction", name="unique direction with map"),
    )
