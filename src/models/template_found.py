from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.region import Region


class TemplateFoundPlacement(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    template_found_map_id: Mapped[int] = mapped_column(
        ForeignKey("template_found_map.id"), nullable=False
    )
    template_found_map: Mapped["TemplateFoundMap"] = relationship(
        back_populates="templates_found_placement"
    )
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"), nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    region: Mapped[Region] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "template_found_map_id", "region_id", name="unique template found place"
        ),
    )

    def __str__(self) -> str:
        return self.filename

    def __repr__(self) -> str:
        return self.__str__()


class TemplateFoundMap(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    map_id: Mapped[int | None] = mapped_column(ForeignKey("map.id"), nullable=True)
    template_found_id: Mapped[int] = mapped_column(
        ForeignKey("template_found.id"), nullable=False
    )
    parsed_count: Mapped[int] = mapped_column(nullable=False, default=0)
    templates_found_placement: Mapped[List["TemplateFoundPlacement"]] = relationship(
        back_populates="template_found_map"
    )

    def __hash__(self) -> int:
        return self.id.__hash__()

    __table_args__ = (
        UniqueConstraint(
            "map_id", "template_found_id", name="unique template map found"
        ),
    )


class TemplateFound(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    templates_found_map: Mapped[List["TemplateFoundMap"]] = relationship()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
