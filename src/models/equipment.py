from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.rune import Line


class Equipment(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    lines: Mapped[list[Line]] = relationship(
        cascade="all, delete-orphan", foreign_keys=[Line.equipment_id]
    )
    exo_line_id: Mapped[int] = mapped_column(ForeignKey("line.id"), nullable=True)
    exo_line: Mapped["Line"] = relationship(foreign_keys=[exo_line_id])

    __table_args__ = (
        UniqueConstraint("label", "user_id", name="unique label for user"),
    )
