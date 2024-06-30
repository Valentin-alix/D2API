from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.item import Item
from src.models.job import Job
from src.models.map import Map


class Collectable(Base):
    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), unique=True)
    item: Mapped[Item] = relationship()

    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"))
    job: Mapped[Job] = relationship()

    def __hash__(self) -> int:
        return self.id.__hash__()

    def __str__(self) -> str:
        return self.item.name

    def __repr__(self) -> str:
        return self.__str__()


class CollectableMapInfo(Base):
    collectable_id: Mapped[int] = mapped_column(
        ForeignKey("collectable.id"), primary_key=True
    )
    map_id: Mapped[int] = mapped_column(ForeignKey("map.id"), primary_key=True)
    collectable: Mapped[Collectable] = relationship()
    map: Mapped[Map] = relationship(back_populates="collectables_map_info")
    count: Mapped[int] = mapped_column(nullable=False, default=0)
