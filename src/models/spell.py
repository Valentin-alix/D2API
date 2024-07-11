from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from D2Shared.shared.enums import CharacteristicEnum, ElemEnum
from src.models.base import Base


class Spell(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), nullable=False
    )
    index: Mapped[int] = mapped_column(nullable=False)
    elem: Mapped[ElemEnum] = mapped_column(nullable=False)
    is_disenchantment: Mapped[bool] = mapped_column(nullable=False)
    boost_char: Mapped[CharacteristicEnum] = mapped_column(nullable=True)
    is_healing: Mapped[bool] = mapped_column(nullable=False)
    is_for_enemy: Mapped[bool] = mapped_column(nullable=False)
    ap_cost: Mapped[int] = mapped_column(nullable=False)
    max_cast: Mapped[int] = mapped_column(nullable=False)
    min_range: Mapped[int] = mapped_column(nullable=False)
    range: Mapped[int] = mapped_column(nullable=False)
    duration_boost: Mapped[int] = mapped_column(nullable=False)
    boostable_range: Mapped[bool] = mapped_column(nullable=False)
    level: Mapped[int] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    __table_args__ = (
        UniqueConstraint("character_id", "index", name="unique index per character"),
        CheckConstraint(
            "level>=1 AND level<=200",
            name="check legit spell lvl",
        ),
    )
