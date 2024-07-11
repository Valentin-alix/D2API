from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.enums import CharacteristicEnum, ElemEnum
from D2Shared.shared.schemas.character import CharacterSchema
from D2Shared.shared.schemas.spell_lvl import (
    CurrentBoostSchema,
    SpellSchema,
)
from src.database import session_local
from src.models.character import Character
from src.models.spell import Spell
from src.queries.spell import (
    choose_spells,
    get_max_range_valuable_dmg_spell,
    get_spell_lvl_for_boost,
    is_boost_for_characteristic,
)
from src.security.auth import login

router = APIRouter(prefix="/spell", dependencies=[Depends(login)])


@router.get("/", response_model=list[SpellSchema])
def get_spells(character_id: int, session: Session = Depends(session_local)):
    character = session.get_one(Character, character_id)
    spell_lvls = session.query(Spell).filter(
        Spell.character_id == character_id, Spell.level <= character.lvl
    )
    return spell_lvls


@router.get("/spell/for_boost/", response_model=SpellSchema | None)
def spell_for_boost(
    character_id: int,
    characteristic: CharacteristicEnum,
    session: Session = Depends(session_local),
):
    spell_lvl = get_spell_lvl_for_boost(
        session.get_one(Character, character_id), characteristic, session
    )
    return spell_lvl


@router.get(
    "/spell/{spell_id}/is_boost_for_char/",
    response_model=bool,
)
def is_spell_boost_for_char(
    spell_id: int,
    characteristic: CharacteristicEnum,
    session: Session = Depends(session_local),
):
    return is_boost_for_characteristic(session.get_one(Spell, spell_id), characteristic)


@router.get("/spell/max_range_valuable_dmg_spell/", response_model=int)
def max_range_valuable_dmg_spell(
    prefered_elem: ElemEnum,
    po_bonus: int,
    spell_ids: list[int],
    session: Session = Depends(session_local),
):
    max_range_spell = get_max_range_valuable_dmg_spell(
        session, prefered_elem, po_bonus, spell_ids
    )
    return max_range_spell


@router.get("/spell/best_combination/", response_model=list[SpellSchema])
def get_best_combination(
    dist_from_enemy: float | None,
    spell_ids: list[int],
    useful_boost_chars: list[CharacteristicEnum],
    use_heal: bool,
    character: CharacterSchema,
    pa: int,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
    session: Session = Depends(session_local),
):
    related_spells = session.query(Spell).filter(Spell.id.in_(spell_ids)).all()
    bests_combination = choose_spells(
        dist_from_enemy,
        related_spells,
        useful_boost_chars,
        character,
        pa,
        use_heal,
        spell_used_ids_with_count,
        current_boosts,
    )
    return bests_combination
