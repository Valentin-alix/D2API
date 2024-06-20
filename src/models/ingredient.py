from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.items.item import Item
    from src.models.recipe import Recipe


class Ingredient(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), nullable=False)
    item: Mapped["Item"] = relationship()
    quantity: Mapped[int] = mapped_column(nullable=False)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")

    __table_args__ = (
        UniqueConstraint("item_id", "recipe_id", name="unique ingredient on recipe"),
    )

    def __str__(self) -> str:
        return f"{self.item.name}*{self.quantity}"

    def __repr__(self) -> str:
        return self.__str__()
