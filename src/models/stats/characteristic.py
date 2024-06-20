from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CharacteristicCategory(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class Characteristic(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=True)
    characteristic_category_id: Mapped[int] = mapped_column(
        ForeignKey("characteristic_category.id"), nullable=True
    )
    characteristic_category: Mapped[CharacteristicCategory | None] = relationship()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
