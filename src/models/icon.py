from __future__ import annotations

from sqlalchemy import Column, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Icon(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    image = Column(LargeBinary, nullable=False)
