from __future__ import annotations
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    sub_expire: Mapped[datetime] = mapped_column(default=datetime(2100, 1, 1))

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.id.__hash__()
