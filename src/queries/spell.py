from random import shuffle

from D2Shared.shared.enums import CharacteristicEnum
from D2Shared.shared.schemas.spell import CurrentBoostSchema
from src.models.character import Character
from src.models.spell import Spell


def choose_spells(
    dist_from_enemy: float | None,
    spells: list[Spell],
    useful_boost_chars: list[CharacteristicEnum],
    character: Character,
    pa: int,
    use_heal: bool,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
) -> list[Spell]:
    best_combination = get_best_combination_spells(
        dist_from_enemy,
        character,
        spells,
        useful_boost_chars,
        use_heal,
        pa,
        spell_used_ids_with_count,
        current_boosts,
    )
    best_combination_ordered = get_best_order_spells(best_combination)
    return best_combination_ordered


def get_range_spell(character: Character, spell: Spell) -> int:
    if spell.boostable_range:
        return character.po_bonus + spell.range
    return spell.range


def get_best_combination_spells(
    dist_from_enemy: float | None,
    character: Character,
    spells: list[Spell],
    useful_boost_chars: list[CharacteristicEnum],
    use_heal: bool,
    pa: int,
    spell_used_ids_with_count: dict[int, int],
    current_boosts: set[CurrentBoostSchema],
) -> list[Spell]:
    """get best combination of spells based on total pa consumed & elem

    Args:
        spells (list[tuple[Spell, ...]]): spells
        elem (Elem): the prefered elem targeted

    Returns:
        tuple[Spell, ...]: the best combination of spell found
    """

    def is_valid_spell(spell: Spell) -> bool:
        if not spell.is_for_enemy and not spell.boost_char and not spell.is_healing:
            return False

        if spell.is_healing and not use_heal:
            return False

        if spell.is_for_enemy and (
            not dist_from_enemy
            or get_range_spell(character, spell) < dist_from_enemy
            or spell.min_range > dist_from_enemy
        ):
            return False

        if spell.boost_char and not any(
            spell.boost_char == char for char in useful_boost_chars
        ):
            return False

        return True

    def get_weigh_spell(spell: Spell) -> float:
        weight: float = 0

        if spell.boost_char:
            curr_boost_spell_id = (boost.spell_level_id for boost in current_boosts)
            if spell.id not in curr_boost_spell_id:
                weight += 1

        elif spell.is_for_enemy:
            weight += 2
            if spell.elem == character.elem:
                weight += 5

        return weight

    spells = [spell_lvl for spell_lvl in spells if is_valid_spell(spell_lvl)]
    shuffle(spells)

    total_pa_combination: int = 0
    best_combination: list[Spell] = []
    spells.sort(key=lambda spell_lvl: get_weigh_spell(spell_lvl), reverse=True)

    for spell_lvl in spells:
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
    combination: list[Spell],
) -> list[Spell]:
    """get best order of spell based on disenchantement, boost

    Args:
        combination (tuple[Spell, ...]): the best combination of spell found

    Returns:
        list[Spell]: the combination of spell with good order
    """
    return sorted(
        combination,
        key=lambda spell: (spell.is_disenchantment, spell.boost_char is None),
        reverse=True,
    )
