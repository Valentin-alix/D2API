from src.models.base import Base
from src.models.job import Job


from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CharacterJobInfo(Base):
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), primary_key=True)
    job: Mapped["Job"] = relationship()

    lvl: Mapped[int] = mapped_column(nullable=False, default=1)
    weight: Mapped[float] = mapped_column(nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("lvl>=1 AND lvl<=200", name="check legit character job lvl"),
    )
