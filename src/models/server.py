from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Server(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
