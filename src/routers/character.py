from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.character import (
    CharacterSchema,
    UpdateCharacterSchema,
)
from D2Shared.shared.schemas.character_job_info import CharacterJobInfoSchema
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.item import SellItemInfo
from D2Shared.shared.schemas.spell import SpellSchema, UpdateSpellSchema
from src.database import session_local
from src.models.character import Character
from src.models.character_job_info import CharacterJobInfo
from src.models.character_sell_item_info import CharacterSellItemInfo
from src.models.item import Item
from src.models.recipe import Recipe
from src.models.spell import Spell
from src.models.sub_area import SubArea
from src.models.waypoint import Waypoint
from src.queries.character import (
    get_possible_collectable,
    populate_job_info,
    populate_sub_areas,
)
from src.queries.utils import get_or_create
from src.security.auth import login

router = APIRouter(prefix="/character", dependencies=[Depends(login)])


@router.put("/{character_id}", response_model=CharacterSchema)
def update_character(
    character_id: str,
    character_update: UpdateCharacterSchema,
    session: Session = Depends(session_local),
):
    character = session.get(Character, character_id)
    character_data = character_update.model_dump(exclude_unset=True)
    for key, value in character_data.items():
        setattr(character, key, value)
    session.commit()
    return character


@router.put("/{character_id}/job_infos")
def update_job_infos(
    character_id: str,
    job_info_datas: list[CharacterJobInfoSchema],
    session: Session = Depends(session_local),
):
    for job_info_data in job_info_datas:
        job_info = (
            session.query(CharacterJobInfo)
            .filter(
                CharacterJobInfo.character_id == character_id,
                CharacterJobInfo.job_id == job_info_data.job_id,
            )
            .one()
        )
        job_info.lvl = job_info_data.lvl
        job_info.weight = job_info_data.weight
    session.commit()


@router.put("/{character_id}/waypoints")
def update_waypoints(
    character_id: str,
    waypoint_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    waypoints = session.query(Waypoint).filter(Waypoint.id.in_(waypoint_ids)).all()
    character.waypoints = waypoints
    session.commit()


@router.put("/{character_id}/recipes")
def update_recipes(
    character_id: str,
    recipe_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    recipes = session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    character.recipes = recipes
    session.commit()


@router.put("/{character_id}/sell_items/")
def update_sell_items(
    character_id: str,
    items_info: list[SellItemInfo],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    character_sell_items_info: list[CharacterSellItemInfo] = []
    for item_info in items_info:
        sell_item_info, is_created = get_or_create(
            session,
            CharacterSellItemInfo,
            commit=True,
            character_id=character_id,
            item_id=item_info.item_id,
            defaults={"sale_hotel_quantities": item_info.sale_hotel_quantities},
        )
        if not is_created:
            sell_item_info.sale_hotel_quantities = item_info.sale_hotel_quantities
        character_sell_items_info.append(sell_item_info)

    character.sell_items_infos = character_sell_items_info
    session.commit()


@router.put("/{character_id}/spells/", response_model=list[SpellSchema])
def update_spells(
    character_id: str,
    spells_data: list[UpdateSpellSchema],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    related_spells: list[Spell] = []
    for spell_data in spells_data:
        related_spell = get_or_create(
            session,
            Spell,
            commit=True,
            character_id=spell_data.character_id,
            index=spell_data.index,
            defaults=spell_data.model_dump(),
        )[0]
        for key, value in spell_data.model_dump(exclude_unset=True).items():
            setattr(related_spell, key, value)
        related_spells.append(related_spell)
    character.spells = related_spells
    session.commit()
    return character.spells


@router.put("/{character_id}/sub_areas")
def update_sub_areas(
    character_id: str,
    sub_area_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    sub_areas = session.query(SubArea).filter(SubArea.id.in_(sub_area_ids)).all()
    character.sub_areas = sub_areas
    session.commit()


@router.post("/{character_id}/bank_items")
def add_bank_items(
    character_id: str,
    item_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    items = session.query(Item).filter(Item.id.in_(item_ids)).all()
    character.bank_items.extend(items)
    session.commit()


@router.delete("/{character_id}/bank_items")
def remove_bank_items(
    character_id: str,
    item_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    items = session.query(Item).filter(Item.id.in_(item_ids)).all()
    for item in items:
        if item in character.bank_items:
            character.bank_items.remove(item)
    session.commit()


@router.get(
    "/{character_id}/possible_collectable", response_model=list[CollectableSchema]
)
def get_char_possible_collectable(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    return get_possible_collectable(session, character.harvest_jobs_infos)


@router.get("/{character_id}/or_create/", response_model=CharacterSchema)
def get_or_create_character(
    character_id: str,
    session: Session = Depends(session_local),
):
    character, is_created = get_or_create(
        session,
        Character,
        id=character_id,
        defaults={"server_id": 1},
    )
    if is_created:
        populate_job_info(session, character.id)
        populate_sub_areas(session, character)
    return character
