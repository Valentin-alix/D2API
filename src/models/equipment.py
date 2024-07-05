from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.rune import Line


from sqlalchemy.orm import Mapped, mapped_column, relationship


class Equipment(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    lines: Mapped[list["Line"]] = relationship(back_populates="equipment")

    __table_args__ = (
        UniqueConstraint("label", "user_id", name="unique label for user"),
    )
