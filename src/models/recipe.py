from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.ingredient import Ingredient
    from src.models.item import Item
    from src.models.job import Job


class Recipe(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    result_item_id: Mapped[int] = mapped_column(
        ForeignKey("item.id"), nullable=False, unique=True
    )
    result_item: Mapped["Item"] = relationship(
        back_populates="recipe", single_parent=True
    )
    ingredients: Mapped[List["Ingredient"]] = relationship(back_populates="recipe")
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), nullable=False)
    job: Mapped["Job"] = relationship()

    def __str__(self) -> str:
        return self.result_item.name

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.result_item_id.__hash__()

    @property
    def receipe_pod_cost(self) -> int:
        return sum(
            ingredient.item.weight * ingredient.quantity
            for ingredient in self.ingredients
        )
