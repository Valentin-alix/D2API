from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.item import Item

if TYPE_CHECKING:
    from src.models.monster import Monster


class Drop(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monster.id"), nullable=False)
    monster: Mapped["Monster"] = relationship(back_populates="drops")
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), nullable=False)
    item: Mapped[Item] = relationship()
    percentage: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (UniqueConstraint("monster_id", "item_id", name="unique drop"),)

    def __str__(self) -> str:
        return f"{self.item}"

    def __repr__(self) -> str:
        return self.__str__()
