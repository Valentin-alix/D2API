import json

from sqlalchemy.orm import Session, joinedload, selectinload
from tqdm import tqdm

from D2Shared.shared.enums import DispellableEnum, ElemEnum
from scripts.populate.dofus.consts import (
    D2O_BREED_PATH,
    D2O_EFFECTS_PATH,
    D2O_SPELL_LEVELS_PATH,
    D2O_SPELL_VARIANT_PATH,
    D2O_SPELLS_PATH,
)
from src.models.breed import Breed
from src.models.characteristic import Characteristic
from src.models.effect import Effect
from src.models.spell import (
    Spell,
    SpellLevel,
    SpellLevelEffect,
    SpellVariant,
)
from src.queries.spell import get_index_spell


def init_breed(session: Session, d2i_texts: dict):
    print("importing breeds...")
    if session.query(Breed).first() is not None:
        return

    with open(D2O_BREED_PATH, encoding="utf8") as file:
        breeds = json.load(file)
        breeds_entities: list[Breed] = []
        for breed in tqdm(breeds):
            breeds_entities.append(
                Breed(id=breed["id"], name=d2i_texts.get(str(breed["shortNameId"])))
            )
        session.add_all(breeds_entities)
        session.commit()


def init_effects_spell(session: Session, d2i_texts: dict):
    # session.query(SpellLevelEffect).delete()
    # session.query(Effect).delete()
    # session.query(SpellLevel).delete()
    # session.query(Spell).delete()
    # session.query(SpellVariant).delete()

    print("importing effects...")
    if session.query(Effect).first() is not None:
        return

    with open(D2O_EFFECTS_PATH, encoding="utf8") as file:
        effects: list[dict] = json.load(file)
        valid_characteristic_ids: list[int] = [
            elem[0] for elem in session.query(Characteristic.id).all()
        ]
        effects_entities: list[Effect] = []
        for effect in tqdm(effects):
            effects_entities.append(
                Effect(
                    id=effect["id"],
                    characteristic_id=(
                        effect["characteristic"]
                        if effect["characteristic"] in valid_characteristic_ids
                        else None
                    ),
                    is_boost=effect["boost"],
                    description=d2i_texts.get(str(effect["descriptionId"])),
                    operator=effect["operator"],
                    elem=(
                        effect["elementId"] if effect["elementId"] in ElemEnum else None
                    ),
                    use_in_fight=effect["useInFight"],
                )
            )

    session.add_all(effects_entities)
    session.commit()


def init_spells_and_variant(session: Session, d2i_texts: dict):
    print("importing spell variant...")
    if session.query(SpellVariant).first() is not None:
        return

    with open(D2O_SPELL_VARIANT_PATH, encoding="utf8") as file:
        spell_variants = json.load(file)
        valid_breed_ids: list[int] = [elem[0] for elem in session.query(Breed.id).all()]
        spell_variants_entities: list[SpellVariant] = []
        for spell_variant in tqdm(spell_variants):
            if spell_variant["breedId"] not in valid_breed_ids:
                continue
            spell_variant_entity = SpellVariant(
                id=spell_variant["id"],
                breed_id=spell_variant["breedId"],
            )
            spell_variants_entities.append(spell_variant_entity)

        print("importing spells...")
        valid_spell_variant_ids: list[int] = [
            elem.id for elem in spell_variants_entities
        ]
        with open(D2O_SPELLS_PATH, encoding="utf8") as file:
            spells = json.load(file)
            spells_entities: list[Spell] = []
            for spell in tqdm(spells):
                related_spell_variant_id = next(
                    (
                        elem["id"]
                        for elem in spell_variants
                        if spell["id"] in elem["spellIds"]
                    ),
                    None,
                )
                if (
                    related_spell_variant_id is None
                    or related_spell_variant_id not in valid_spell_variant_ids
                ):
                    continue

                spells_entities.append(
                    Spell(
                        id=spell["id"],
                        name=d2i_texts.get(str(spell["nameId"])),
                        spell_variant_id=related_spell_variant_id,
                    )
                )
        session.add_all(spell_variants_entities)
        session.add_all(spells_entities)
        session.commit()


def init_spell_levels(session: Session):
    print("importing spells levels...")
    if session.query(SpellLevel).first() is not None:
        return

    with open(D2O_SPELL_LEVELS_PATH, encoding="utf8") as file:
        spell_levels = json.load(file)
        spell_levels_entities: list[SpellLevel] = []
        spell_effects_entities: list[SpellLevelEffect] = []

        effects_by_id: dict[int, Effect] = {
            elem.id: elem for elem in session.query(Effect).all()
        }
        valid_spell_ids: list[int] = [elem[0] for elem in session.query(Spell.id).all()]

        for spell_level in tqdm(spell_levels):
            if spell_level["spellId"] not in valid_spell_ids:
                continue

            if spell_level["maxCastPerTarget"] == 0:
                max_cast = spell_level["maxCastPerTurn"]
            else:
                max_cast = spell_level["maxCastPerTarget"]

            is_disenchantment = False
            is_boost = False
            is_healing = False
            for spell_effect in spell_level["effects"]:
                related_effect = effects_by_id[spell_effect["effectId"]]
                if "Durée des effets" in related_effect.description:
                    is_disenchantment = True

                if (
                    spell_level["minRange"] == 0
                    and related_effect.is_boost
                    and related_effect.operator == "+"
                ):
                    is_boost = True

                if "Soin" in related_effect.description:
                    is_healing = True

            on_enemy = False
            duration_boost: int = 0
            for spell_effect in spell_level["effects"]:
                related_effect = effects_by_id[spell_effect["effectId"]]
                if (
                    not is_boost
                    and not spell_level["needFreeCell"]
                    and "dommages" in related_effect.description.lower()
                    or "vol" in related_effect.description.lower()
                ):
                    on_enemy = True
                if is_boost:
                    duration_boost = spell_effect["duration"]

            spell_levels_entities.append(
                SpellLevel(
                    id=spell_level["id"],
                    spell_id=spell_level["spellId"],
                    ap_cost=spell_level["apCost"],
                    min_range=spell_level["minRange"],
                    range=spell_level["range"],
                    can_cast_in_line=spell_level["castInLine"],
                    can_cast_in_diagonal=spell_level["castInDiagonal"],
                    need_los=spell_level["castTestLos"],
                    is_disenchantment=is_disenchantment,
                    is_boost=is_boost,
                    is_healing=is_healing,
                    on_enemy=on_enemy,
                    duration_boost=duration_boost,
                    need_free_cell=spell_level["needFreeCell"],
                    need_taken_cell=spell_level["needTakenCell"],
                    need_visible_entity=spell_level["needVisibleEntity"],
                    range_can_be_boosted=spell_level["rangeCanBeBoosted"],
                    max_stack=spell_level["maxStack"],
                    max_cast=max_cast,
                    min_cast_interval=spell_level["minCastInterval"],
                    initial_cooldown=spell_level["initialCooldown"],
                    global_cooldown=spell_level["globalCooldown"],
                    min_player_level=spell_level["minPlayerLevel"],
                )
            )

            for spell_lvl_effect in spell_level["effects"]:
                if spell_lvl_effect["dispellable"] != DispellableEnum.IS_DISPELLABLE:
                    continue
                spell_effects_entities.append(
                    SpellLevelEffect(
                        spell_level_id=spell_level["id"],
                        duration=spell_lvl_effect["duration"],
                        effect_id=spell_lvl_effect["effectId"],
                        dispellable=spell_lvl_effect["dispellable"],
                    )
                )

        session.add_all(spell_levels_entities)
        session.add_all(spell_effects_entities)
        session.commit()


def init_spell_lvl_index(session: Session):
    for spell in (
        session.query(Spell)
        .join(SpellLevel, SpellLevel.spell_id == Spell.id)
        .options(selectinload(Spell.spell_levels), joinedload(Spell.spell_variant))
        .all()
    ):
        spell.default_index = get_index_spell(session, spell)
    session.commit()
