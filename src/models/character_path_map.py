from src.models.base import Base


from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CharacterPathMap(Base):
    character_path_info_id: Mapped[int] = mapped_column(
        ForeignKey("character_path_info.id", ondelete="CASCADE"), primary_key=True
    )
    map_id: Mapped[int] = mapped_column(ForeignKey("map.id"), primary_key=True)
    order_index: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "character_path_info_id",
            "order_index",
            name="unique order index for same path info",
        ),
    )
