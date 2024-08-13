from D2Shared.shared.enums import SaleHotelQuantity
from src.models.base import Base
from src.models.item import Item


from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CharacterSellItemInfo(Base):
    character_id: Mapped[str] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)
    item: Mapped["Item"] = relationship()
    sale_hotel_quantities: Mapped[list[SaleHotelQuantity]] = mapped_column(
        ARRAY(Enum(SaleHotelQuantity)),
        nullable=False,
    )
