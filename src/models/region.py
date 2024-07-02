from operator import and_

from sqlalchemy import CheckConstraint, ColumnElement, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, mapped_column

from D2Shared.shared.schemas.region import RegionSchema
from src.models.base import Base


class Region(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    left: Mapped[int] = mapped_column(nullable=False)
    right: Mapped[int] = mapped_column(nullable=False)
    top: Mapped[int] = mapped_column(nullable=False)
    bot: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint("left>=0 and left<=1920", name="check legit left"),
        CheckConstraint("right>=0 and right<=1920", name="check legit right"),
        CheckConstraint("top>=0 and top<=1080", name="check legit top"),
        CheckConstraint("bot>=0 and bot<=1080", name="check legit bot"),
    )

    @hybrid_method
    def is_enclosing(self, region: "RegionSchema|Region") -> bool:  # type: ignore
        return (
            self.left <= region.left
            and self.right >= region.right
            and self.top <= region.top
            and self.bot >= region.bot
        )

    @is_enclosing.expression
    @classmethod
    def is_enclosing(cls, region: "RegionSchema|Region") -> ColumnElement[bool]:
        return and_(
            and_(cls.left <= region.left, cls.right >= region.right),
            and_(cls.top <= region.top, cls.bot >= region.bot),
        )

    __table_args__ = (
        UniqueConstraint("left", "right", "top", "bot", name="unique region"),
    )

    def __str__(self) -> str:
        return f"top : {self.top}, bot : {self.bot}, right : {self.right}, left : {self.left}"

    def __repr__(self) -> str:
        return self.__str__()
