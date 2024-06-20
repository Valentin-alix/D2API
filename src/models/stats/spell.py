from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from EzreD2Shared.shared.enums import DispellableEnum
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.stats.breed import Breed
    from src.models.stats.effect import Effect


class SpellVariant(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    breed_id: Mapped[int] = mapped_column(ForeignKey("breed.id"), nullable=False)
    breed: Mapped["Breed"] = relationship(back_populates="spell_variants")
    spells: Mapped[List[Spell]] = relationship(back_populates="spell_variant")


class Spell(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    spell_variant_id: Mapped[int] = mapped_column(
        ForeignKey("spell_variant.id"), nullable=False
    )
    spell_variant: Mapped[SpellVariant] = relationship(back_populates="spells")
    spell_levels: Mapped[List[SpellLevel]] = relationship(back_populates="spell")
    default_index: Mapped[int] = mapped_column(nullable=False, default=0)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class SpellLevel(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    spell_id: Mapped[int] = mapped_column(ForeignKey("spell.id"), nullable=False)
    spell: Mapped[Spell] = relationship(back_populates="spell_levels")
    ap_cost: Mapped[int] = mapped_column(nullable=False)
    max_cast: Mapped[int] = mapped_column(nullable=False)
    min_range: Mapped[int] = mapped_column(nullable=False)
    range: Mapped[int] = mapped_column(nullable=False)
    can_cast_in_line: Mapped[bool] = mapped_column(nullable=False)
    can_cast_in_diagonal: Mapped[bool] = mapped_column(nullable=False)
    need_los: Mapped[bool] = mapped_column(nullable=False)

    is_disenchantment: Mapped[bool] = mapped_column(nullable=False)
    is_boost: Mapped[bool] = mapped_column(nullable=False)
    is_healing: Mapped[bool] = mapped_column(nullable=False)
    on_enemy: Mapped[bool] = mapped_column(nullable=False)
    duration_boost: Mapped[int] = mapped_column(nullable=False)

    need_free_cell: Mapped[bool] = mapped_column(nullable=False)
    need_taken_cell: Mapped[bool] = mapped_column(nullable=False)
    need_visible_entity: Mapped[bool] = mapped_column(nullable=False)
    range_can_be_boosted: Mapped[bool] = mapped_column(nullable=False)
    max_stack: Mapped[int] = mapped_column(nullable=False)
    min_cast_interval: Mapped[int] = mapped_column(nullable=False)
    initial_cooldown: Mapped[int] = mapped_column(nullable=False)
    global_cooldown: Mapped[int] = mapped_column(nullable=False)
    min_player_level: Mapped[int] = mapped_column(nullable=False)
    spell_lvl_effects: Mapped[List[SpellLevelEffect]] = relationship(
        back_populates="spell_level"
    )

    def __str__(self) -> str:
        return self.spell.name

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.id.__hash__()


class SpellLevelEffect(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    spell_level_id: Mapped[int] = mapped_column(ForeignKey("spell_level.id"))
    spell_level: Mapped[SpellLevel] = relationship(back_populates="spell_lvl_effects")
    effect_id: Mapped[int] = mapped_column(ForeignKey("effect.id"))
    effect: Mapped[Effect] = relationship()
    duration: Mapped[int] = mapped_column(nullable=False)
    dispellable: Mapped[DispellableEnum] = mapped_column(nullable=False)
