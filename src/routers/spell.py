from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.enums import CharacteristicEnum, ElemEnum
from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.spell_lvl import CurrentBoostSchema, SpellLevelSchema
from src.database import session_local
from src.models.spell import SpellLevel
from src.queries.spell import (
    choose_spells,
    get_max_range_valuable_dmg_spell,
    get_ordered_spells_levels,
    get_spell_lvl_for_boost,
    is_boost_for_characteristic,
)
from src.security.auth import login

router = APIRouter(prefix="/spell", dependencies=[Depends(login)])


@router.get("/spell_lvl/", response_model=list[SpellLevelSchema])
def spell_lvls(
    character_lvl: int,
    breed_id: int,
    session: Session = Depends(session_local),
):
    spell_lvls = get_ordered_spells_levels(character_lvl, breed_id, session)
    return spell_lvls


@router.get("/spell_lvl/for_boost/", response_model=SpellLevelSchema | None)
def spell_lvls_for_boost(
    character_lvl: int,
    breed_id: int,
    characteristic: CharacteristicEnum,
    session: Session = Depends(session_local),
):
    spell_lvl = get_spell_lvl_for_boost(
        character_lvl, breed_id, characteristic, session
    )
    return spell_lvl


@router.get(
    "/spell_lvl/{spell_lvl_id}/is_boost_for_char/",
    response_model=bool,
)
def is_spell_lvl_boost_for_char(
    spell_lvl_id: int,
    characteristic: CharacteristicEnum,
    session: Session = Depends(session_local),
):
    return is_boost_for_characteristic(
        session.get_one(SpellLevel, spell_lvl_id), characteristic
    )


@router.get("/spell_lvl/max_range_valuable_dmg_spell", response_model=int)
def max_range_valuable_dmg_spell(
    prefered_elem: ElemEnum,
    po_bonus: int,
    spell_lvl_ids: list[int],
    session: Session = Depends(session_local),
):
    max_range_spell = get_max_range_valuable_dmg_spell(
        session, prefered_elem, po_bonus, spell_lvl_ids
    )
    return max_range_spell


@router.get("/spell_lvl/best_combination/", response_model=list[SpellLevelSchema])
def get_best_combination(
    dist_from_enemy: float | None,
    spell_lvls_ids: list[int],
    useful_boost_chars: list[CharacteristicEnum],
    use_heal: bool,
    character: CharacterSchema,
    pa: int,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
    session: Session = Depends(session_local),
):
    related_spell_lvls = (
        session.query(SpellLevel).filter(SpellLevel.id.in_(spell_lvls_ids)).all()
    )
    bests_combination = choose_spells(
        dist_from_enemy,
        related_spell_lvls,
        useful_boost_chars,
        character,
        pa,
        use_heal,
        spell_used_ids_with_count,
        current_boosts,
    )
    return bests_combination
