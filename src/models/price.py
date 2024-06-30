from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.item import Item
from src.models.server import Server


class Price(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"), nullable=False)

    average: Mapped[float | None] = mapped_column(nullable=False)
    item: Mapped[Item] = relationship()
    server: Mapped[Server] = relationship()

    __table_args__ = (
        UniqueConstraint("item_id", "server_id", name="unique price by server item"),
        CheckConstraint("average>=0", name="check positive price"),
    )
