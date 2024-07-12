from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from D2Shared.shared.consts.areas import UNSUB_AREAS
from src.models.base import Base


class Area(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    @hybrid_property
    def is_for_sub(self) -> bool:  # type: ignore
        return self.name not in UNSUB_AREAS

    @is_for_sub.expression
    def is_for_sub(cls):
        return cls.name.not_in(UNSUB_AREAS)  # type: ignore
