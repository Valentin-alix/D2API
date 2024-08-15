from src.models.base import Base
from src.models.character_path_map import CharacterPathMap


from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


from typing import List


class CharacterPathInfo(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[str] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    path_maps: Mapped[List["CharacterPathMap"]] = relationship(
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("character_id", "name", name="unique path name by character"),
    )
