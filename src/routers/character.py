from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from D2Shared.shared.schemas.collectable import CollectableSchema
from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.spell_lvl import SpellSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from D2Shared.shared.schemas.waypoint import WaypointSchema
from src.database import session_local
from src.models.character import Character, CharacterJobInfo
from src.models.item import Item
from src.models.spell import Spell
from src.models.sub_area import SubArea
from src.models.waypoint import Waypoint
from src.queries.character import (
    get_max_pods_character,
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
    character_update: CharacterSchema,
    session: Session = Depends(session_local),
):
    character = session.get(Character, character_id)
    character_data = character_update.model_dump(exclude_unset=True)
    for key, value in character_data.items():
        setattr(character, key, value)
    session.commit()
    return character


@router.put("/{character_id}/job_info", response_model=CharacterJobInfoSchema)
def update_job_info(
    character_id: str,
    job_id: int,
    lvl: int,
    weight: float | None = None,
    session: Session = Depends(session_local),
):
    job_info = (
        session.query(CharacterJobInfo)
        .filter(
            CharacterJobInfo.character_id == character_id,
            CharacterJobInfo.job_id == job_id,
        )
        .one()
    )
    job_info.lvl = lvl
    if weight is not None:
        job_info.weight = weight
    session.commit()
    return job_info


@router.get("/{character_id}/job_info", response_model=list[CharacterJobInfoSchema])
def get_job_infos(
    character_id: str,
    session: Session = Depends(session_local),
):
    job_infos = (
        session.query(CharacterJobInfo)
        .filter(
            CharacterJobInfo.character_id == character_id,
        )
        .all()
    )
    return job_infos


@router.get("/{character_id}/max_pods", response_model=int)
def get_max_pods(
    character_id: str,
    session: Session = Depends(session_local),
):
    return get_max_pods_character(session, character_id)


@router.post("/{character_id}/waypoint")
def add_waypoint(
    character_id: str,
    waypoint_id: int,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    waypoint = session.get_one(Waypoint, waypoint_id)
    character.waypoints.append(waypoint)
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


@router.put("/{character_id}/spells")
def update_spells(
    character_id: str,
    spells_data: list[SpellSchema],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    related_spells: list[Spell] = []
    for spell_data in spells_data:
        related_spell = get_or_create(
            session,
            Spell,
            commit=False,
            character_id=spell_data.character_id,
            index=spell_data.index,
        )[0]
        for key, value in spell_data.model_dump(exclude_unset=True).items():
            setattr(related_spell, key, value)
        related_spells.append(related_spell)
    character.spells = related_spells
    session.commit()


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


@router.get("/{character_id}/waypoints", response_model=list[WaypointSchema])
def get_waypoints(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    return character.waypoints


@router.get("/{character_id}/sub_areas", response_model=list[SubAreaSchema])
def get_sub_areas(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    return character.sub_areas


@router.get("/{character_id}/bank_items", response_model=list[ItemSchema])
def get_bank_items(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    return character.bank_items


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
