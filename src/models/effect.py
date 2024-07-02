from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from D2Shared.shared.enums import ElemEnum
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.characteristic import Characteristic


class Effect(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    is_boost: Mapped[bool] = mapped_column(nullable=False)
    characteristic_id: Mapped[int] = mapped_column(
        ForeignKey("characteristic.id"), nullable=True
    )
    characteristic: Mapped["Characteristic"] = relationship()
    description: Mapped[str] = mapped_column(nullable=True)
    operator: Mapped[str] = mapped_column(nullable=True)
    elem: Mapped[ElemEnum] = mapped_column(nullable=True)
    use_in_fight: Mapped[bool] = mapped_column(nullable=False)
