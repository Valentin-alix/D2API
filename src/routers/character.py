from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.character import (
    CharacterJobInfoSchema,
    CharacterSchema,
)
from EzreD2Shared.shared.schemas.collectable import CollectableSchema
from EzreD2Shared.shared.schemas.item import ItemSchema
from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from src.database import session_local
from src.models.config.character import Character, CharacterJobInfo
from src.models.items.item import Item
from src.models.navigations.waypoint import Waypoint
from src.queries.character import (
    get_max_pods_character,
    get_possible_collectable,
    populate_job_info,
)
from src.queries.utils import get_or_create

router = APIRouter(prefix="/character")


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
        character.bank_items.remove(item)
    session.commit()


@router.get("/{character_id}/waypoints", response_model=list[WaypointSchema])
def get_waypoints(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    return character.waypoints


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
    return character
