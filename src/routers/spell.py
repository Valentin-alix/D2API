from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.spell import (
    CurrentBoostSchema,
    SpellSchema,
)
from src.database import session_local
from src.models.character import Character
from src.models.spell import Spell
from src.queries.spell import choose_spells
from src.security.auth import login

router = APIRouter(prefix="/spell", dependencies=[Depends(login)])


@router.get("/best_combination/", response_model=list[SpellSchema])
def get_best_combination(
    dist_from_enemy: float | None,
    use_heal: bool,
    pa: int,
    spell_ids: list[int],
    useful_boost_chars: list[CharacteristicEnum],
    character_id: str,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
    session: Session = Depends(session_local),
):
    related_spells = session.query(Spell).filter(Spell.id.in_(spell_ids)).all()
    bests_combination = choose_spells(
        dist_from_enemy,
        related_spells,
        useful_boost_chars,
        session.get_one(Character, character_id),
        pa,
        use_heal,
        spell_used_ids_with_count,
        current_boosts,
    )
    return bests_combination
