from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.icon import Icon
from src.models.items.type_item import TypeItem
from src.models.recipe import Recipe


class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False)
    type_item_id: Mapped[int] = mapped_column(
        ForeignKey("type_item.id"), nullable=False
    )
    type_item: Mapped[TypeItem] = relationship()
    level: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    recipe: Mapped[Recipe] = relationship(back_populates="result_item")
    icon_id: Mapped[int | None] = mapped_column(ForeignKey("icon.id"), nullable=True)
    icon: Mapped[Icon | None] = relationship()
    is_saleable: Mapped[bool] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.id.__hash__()
