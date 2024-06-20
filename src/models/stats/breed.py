from __future__ import annotations

from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.stats.spell import SpellVariant


class Breed(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    spell_variants: Mapped[List[SpellVariant]] = relationship(back_populates="breed")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
