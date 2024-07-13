from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.rune import Line, Stat


class Equipment(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)

    lines: Mapped[list[Line]] = relationship(cascade="all, delete-orphan")
    exo_stat_id: Mapped[int] = mapped_column(ForeignKey("stat.id"), nullable=True)
    exo_stat: Mapped[Stat] = relationship()
    exo_attempt: Mapped[int] = mapped_column(default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("label", "user_id", name="unique label for user"),
    )
