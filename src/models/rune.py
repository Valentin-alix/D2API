from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Stat(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    weight: Mapped[float] = mapped_column(nullable=False)
    runes: Mapped[list[Rune]] = relationship(back_populates="stat")

    __table_args__ = (CheckConstraint("weight>0", name="check positive weight"),)


class Rune(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    stat_id: Mapped[int] = mapped_column(ForeignKey("stat.id"), nullable=False)
    stat: Mapped[Stat] = relationship(back_populates="runes")
    stat_quantity: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "stat_quantity", name="unique name with quantity"),
        CheckConstraint("stat_quantity>0", name="check positive quantity"),
    )


class Line(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(nullable=False)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id"), nullable=False
    )
    equipment: Mapped[Equipment] = relationship(back_populates="lines")
    stat_id: Mapped[int] = mapped_column(ForeignKey("stat.id"), nullable=False)
    stat: Mapped[Stat] = relationship()


class Equipment(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(nullable=False, unique=True)
    lines: Mapped[list[Line]] = relationship(back_populates="equipment")
