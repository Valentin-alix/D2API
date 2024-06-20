from random import shuffle

from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from EzreD2Shared.shared.consts.adaptative.positions import EMPTY_POSITION
from EzreD2Shared.shared.enums import CharacteristicEnum, ElemEnum
from EzreD2Shared.shared.schemas.character import CharacterSchema
from EzreD2Shared.shared.schemas.spell_lvl import CurrentBoostSchema, SpellLevelSchema
from src.models.stats.effect import Effect
from src.models.stats.spell import (
    Spell,
    SpellLevel,
    SpellLevelEffect,
    SpellVariant,
)


def choose_spells(
    dist_from_enemy: float | None,
    spell_lvls: list[SpellLevel],
    useful_boost_chars: list[CharacteristicEnum],
    character: CharacterSchema,
    pa: int,
    use_heal: bool,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
) -> list[SpellLevel]:
    best_combination = get_best_combination_spells(
        dist_from_enemy,
        character,
        spell_lvls,
        useful_boost_chars,
        use_heal,
        pa,
        spell_used_ids_with_count,
        current_boosts,
    )
    best_combination_ordered = get_best_order_spells(best_combination)
    return best_combination_ordered


def get_range_spell(character: CharacterSchema, spell: SpellLevel) -> int:
    if spell.range_can_be_boosted:
        return character.po_bonus + spell.range
    return spell.range


def get_best_combination_spells(
    dist_from_enemy: float | None,
    character: CharacterSchema,
    spells_lvl: list[SpellLevel],
    useful_boost_chars: list[CharacteristicEnum],
    use_heal: bool,
    pa: int,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
) -> list[SpellLevel]:
    """get best combination of spells based on total pa consumed & elem

    Args:
        spells (list[tuple[Spell, ...]]): spells
        elem (Elem): the prefered elem targeted

    Returns:
        tuple[Spell, ...]: the best combination of spell found
    """

    def is_valid_spell(spell_lvl: SpellLevel) -> bool:
        if (
            not spell_lvl.on_enemy
            and not spell_lvl.is_boost
            and not spell_lvl.is_healing
        ):
            return False

        if spell_lvl.is_healing and not use_heal:
            return False

        if spell_lvl.on_enemy and (
            not dist_from_enemy
            or get_range_spell(character, spell_lvl) < dist_from_enemy
            or spell_lvl.min_range > dist_from_enemy
        ):
            return False

        if spell_lvl.is_boost and not any(
            is_boost_for_characteristic(spell_lvl, char) for char in useful_boost_chars
        ):
            return False

        return True

    def is_related_elem(spell_lvl: SpellLevel, elem: ElemEnum) -> bool:
        return any(
            spell_effect.effect.elem == elem
            for spell_effect in spell_lvl.spell_lvl_effects
        )

    def get_weigh_spell(spell_lvl: SpellLevel) -> float:
        weight: float = 0

        if spell_lvl.is_boost:
            curr_boost_spell_id = (boost.spell_level_id for boost in current_boosts)
            if spell_lvl.id not in curr_boost_spell_id:
                weight += 1

        elif spell_lvl.on_enemy:
            weight += 2
            if is_related_elem(spell_lvl, character.elem):
                weight += 5

        return weight

    spells_lvl = [spell_lvl for spell_lvl in spells_lvl if is_valid_spell(spell_lvl)]
    shuffle(spells_lvl)

    total_pa_combination: int = 0
    best_combination: list[SpellLevel] = []
    spells_lvl.sort(key=lambda spell_lvl: get_weigh_spell(spell_lvl), reverse=True)

    for spell_lvl in spells_lvl:
        while True:
            if pa - (total_pa_combination + spell_lvl.ap_cost) < 0:
                break
            if (
                best_combination.count(spell_lvl)
                + spell_used_ids_with_count.get(spell_lvl.id, 0)
                >= spell_lvl.max_cast
            ):
                break
            total_pa_combination += spell_lvl.ap_cost
            best_combination.append(spell_lvl)

    return best_combination


def get_best_order_spells(
    combination: list[SpellLevel],
) -> list[SpellLevel]:
    """get best order of spell based on disenchantement, boost

    Args:
        combination (tuple[Spell, ...]): the best combination of spell found

    Returns:
        list[Spell]: the combination of spell with good order
    """
    return sorted(
        combination,
        key=lambda spell: (spell.is_disenchantment, spell.is_boost),
        reverse=True,
    )


def get_max_range_valuable_dmg_spell(
    session: Session, prefered_elem: ElemEnum, po_bonus: int, spell_lvls_ids: list[int]
) -> int:
    """get max range of dmg spell (prefer same elem)"""

    spell_lvl_range_case = case(
        (
            SpellLevel.range_can_be_boosted,
            SpellLevel.range + po_bonus,
        ),
        else_=SpellLevel.range,
    )

    max_range_prefered_spell = (
        session.query(SpellLevel.range)
        .select_from(Effect)
        .join(
            SpellLevelEffect,
            Effect.id == SpellLevelEffect.effect_id,
        )
        .join(SpellLevel, SpellLevelEffect.spell_level_id == SpellLevel.id)
        .filter(SpellLevel.id.in_(spell_lvls_ids))
        .order_by((Effect.elem == prefered_elem).desc(), spell_lvl_range_case.desc())
        .first()
    )
    assert max_range_prefered_spell is not None

    return max_range_prefered_spell[0]


def get_spell_lvl_for_boost(
    character_lvl: int,
    breed_id: int,
    characteristic: CharacteristicEnum,
    session: Session,
) -> SpellLevel | None:
    spell_lvl = (
        session.query(SpellLevel)
        .select_from(SpellLevelEffect)
        .join(SpellLevel, SpellLevelEffect.spell_level_id == SpellLevel.id)
        .join(Spell, SpellLevel.spell_id == Spell.id)
        .join(SpellVariant, Spell.spell_variant_id == SpellVariant.id)
        .join(Effect, SpellLevelEffect.effect_id == Effect.id)
        .filter(
            SpellVariant.breed_id == breed_id,
            SpellLevel.min_player_level <= character_lvl,
            SpellLevel.is_boost,
            Effect.operator == "+",
            Effect.characteristic_id == characteristic,
        )
        .first()
    )
    return spell_lvl


def is_boost_for_characteristic(
    spell_lvl: SpellLevel, characteristic: CharacteristicEnum
) -> bool:
    return spell_lvl.is_boost and any(
        spell_effect.effect.characteristic_id == characteristic
        and spell_effect.effect.operator == "+"
        for spell_effect in spell_lvl.spell_lvl_effects
    )


def get_index_spell(session: Session, spell: Spell) -> int:
    spell_min_lvl = min(spell.spell_levels, key=lambda elem: elem.min_player_level)
    breed_id = spell.spell_variant.breed_id
    count_spell_before = (
        session.query(Spell)
        .join(SpellLevel, SpellLevel.spell_id == Spell.id)
        .join(SpellVariant, SpellVariant.id == Spell.spell_variant_id)
        .filter(
            SpellVariant.breed_id == breed_id,
        )
        .having(func.min(SpellLevel.min_player_level) <= spell_min_lvl.min_player_level)
        .group_by(Spell.id)
        .count()
    )
    return count_spell_before


def get_ordered_spells_levels(
    character_lvl: int, breed_id: int, session: Session
) -> list[SpellLevel]:
    spells = (
        session.query(Spell)
        .join(SpellLevel, SpellLevel.spell_id == Spell.id)
        .join(SpellVariant, Spell.spell_variant_id == SpellVariant.id)
        .filter(SpellVariant.breed_id == breed_id)
        .group_by(Spell.id)
        .order_by(func.min(SpellLevel.min_player_level))
        .options(joinedload(Spell.spell_levels))
        .all()
    )
    spells_lvls: list[SpellLevel] = []
    for spell in spells:
        valid_spells_lvls = [
            elem
            for elem in spell.spell_levels
            if elem.min_player_level <= character_lvl
        ]
        if len(valid_spells_lvls) == 0:
            break
        curr_spell_lvl = max(
            valid_spells_lvls, key=lambda spell_lvl: spell_lvl.min_player_level
        )
        related_schema = SpellLevelSchema.model_validate(spell.spell_levels[0])
        if related_schema.get_pos_spell() == EMPTY_POSITION:
            break
        spells_lvls.append(curr_spell_lvl)

    return spells_lvls
