from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.item import ItemSchema
from D2Shared.shared.schemas.sub_area import SubAreaSchema
from src.database import session_local
from src.models.character import Character
from src.models.collectable import Collectable
from src.models.map import Map
from src.models.sub_area import SubArea
from src.queries.sub_area import (
    get_dropable_items,
    get_max_time_fighter,
    get_max_time_harvester,
    get_random_grouped_sub_area,
    get_valid_sub_areas_fighter,
    get_valid_sub_areas_harvester,
    get_weights_fight_map,
    get_weights_harvest_map,
)
from src.security.auth import login

router = APIRouter(prefix="/sub_area", dependencies=[Depends(login)])


@router.get("/", response_model=list[SubAreaSchema])
def get_sub_areas(
    session: Session = Depends(session_local),
):
    sub_areas = (
        session.query(SubArea)
        .join(Map, Map.sub_area_id == SubArea.id)
        .filter(Map.world_id == 1)
        .all()
    )
    return sub_areas


@router.get("/random_grouped_sub_area/", response_model=list[SubAreaSchema])
def random_grouped_sub_area(
    sub_area_ids_farming: list[int],
    weight_by_map: dict[int, float],
    valid_sub_area_ids: list[int],
    is_sub: bool,
    session: Session = Depends(session_local),
):
    valid_sub_areas = (
        session.query(SubArea).filter(SubArea.id.in_(valid_sub_area_ids)).all()
    )
    return get_random_grouped_sub_area(
        session, sub_area_ids_farming, weight_by_map, valid_sub_areas, is_sub
    )


@router.get("/weights_fight_map", response_model=dict[int, float])
def weights_fight_map(
    server_id: int,
    sub_area_ids: list[int],
    lvl: int,
    session: Session = Depends(session_local),
):
    return get_weights_fight_map(
        session,
        server_id,
        session.query(SubArea).filter(SubArea.id.in_(sub_area_ids)).all(),
        lvl,
    )


@router.get("/max_time_fighter", response_model=int)
def max_time_fighter(
    sub_area_ids: list[int],
    session: Session = Depends(session_local),
):
    return get_max_time_fighter(
        session, session.query(SubArea).filter(SubArea.id.in_(sub_area_ids)).all()
    )


@router.get("/valid_sub_areas_fighter/", response_model=list[SubAreaSchema])
def valid_sub_areas_fighter(
    character_id: str,
    session: Session = Depends(session_local),
):
    return get_valid_sub_areas_fighter(
        session, session.get_one(Character, character_id)
    )


@router.get("/weights_harvest_map", response_model=dict[int, float])
def weights_harvest_map(
    character_id: str,
    server_id: int,
    possible_collectable_ids: list[int],
    valid_sub_area_ids: list[int],
    session: Session = Depends(session_local),
):
    possible_collectables = (
        session.query(Collectable)
        .filter(Collectable.id.in_(possible_collectable_ids))
        .all()
    )
    valid_sub_areas = (
        session.query(SubArea).filter(SubArea.id.in_(valid_sub_area_ids)).all()
    )
    character = session.get_one(Character, character_id)
    weight_by_job_ids = {
        elem.job_id: elem.weight for elem in character.harvest_jobs_infos
    }
    return get_weights_harvest_map(
        session, server_id, possible_collectables, valid_sub_areas, weight_by_job_ids
    )


@router.get("/max_time_harvester", response_model=int)
def max_time_harvester(
    sub_area_ids: list[int],
    session: Session = Depends(session_local),
):
    return get_max_time_harvester(
        session, session.query(SubArea).filter(SubArea.id.in_(sub_area_ids)).all()
    )


@router.get("/valid_sub_areas_harvester/", response_model=list[SubAreaSchema])
def valid_sub_areas_harvester(
    character_id: str,
    session: Session = Depends(session_local),
):
    return get_valid_sub_areas_harvester(
        session, session.get_one(Character, character_id)
    )


@router.get("/{sub_area_id}/dropable_items", response_model=list[ItemSchema])
def dropable_items(
    sub_area_id: int,
    session: Session = Depends(session_local),
):
    return get_dropable_items(session, sub_area_id)
