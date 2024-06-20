from sqlalchemy.orm import Mapped, mapped_column

from EzreD2Shared.shared.enums import CategoryEnum
from src.models.base import Base


class TypeItem(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    category: Mapped[CategoryEnum] = mapped_column(nullable=False)

    def __str__(self) -> str:
        return self.name
