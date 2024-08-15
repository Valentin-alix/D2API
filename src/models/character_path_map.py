from src.models.base import Base


from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.map import Map


class CharacterPathMap(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_path_info_id: Mapped[int] = mapped_column(
        ForeignKey("character_path_info.id", ondelete="CASCADE")
    )
    map_id: Mapped[int] = mapped_column(ForeignKey("map.id"))
    map: Mapped[Map] = relationship()
    order_index: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "character_path_info_id",
            "order_index",
            name="unique order index for same path info",
        ),
    )
