import logging

from fastapi import APIRouter, Depends
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session

from D2Shared.shared.enums import FromDirection
from D2Shared.shared.schemas.map import CoordinatesMapSchema, MapSchema
from D2Shared.shared.schemas.map_direction import MapDirectionSchema
from D2Shared.shared.schemas.map_with_action import MapWithActionSchema
from src.database import session_local
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.queries.astar_maps import AstarMap
from src.queries.map import (
    get_limit_maps_sub_area_id,
    get_map_from_hud,
    get_near_map_allowing_havre,
    get_neighbors,
    get_related_map,
)
from src.security.auth import login

router = APIRouter(prefix="/map", dependencies=[Depends(login)])

logger = logging.getLogger()


@router.get("/{map_id}", response_model=MapSchema)
def map(
    map_id: int,
    session: Session = Depends(session_local),
):
    return session.get_one(Map, map_id)


@router.put("/{map_id}/does_not_allow_teleport_from/", response_model=MapSchema)
def does_not_allow_teleport_from(
    map_id: int,
    session: Session = Depends(session_local),
):
    map = session.get_one(Map, map_id)
    map.allow_teleport_from = False
    session.commit()
    return map


@router.get("/related/", response_model=MapSchema)
def related_map(
    coordinate_map_schema: CoordinatesMapSchema,
    session: Session = Depends(session_local),
):
    return get_related_map(
        session,
        x=coordinate_map_schema.x,
        y=coordinate_map_schema.y,
        world_id=coordinate_map_schema.world_id,
    )


@router.get("/find_path/", response_model=list[MapWithActionSchema] | None)
def find_path(
    use_transport: bool,
    map_id: int,
    from_direction: FromDirection,
    available_waypoints_ids: list[int],
    target_map_ids: list[int],
    session: Session = Depends(session_local),
):
    astar_map = AstarMap(use_transport, available_waypoints_ids, session)
    path_map = astar_map.find_path(
        session.get_one(Map, map_id),
        from_direction,
        session.query(Map).filter(Map.id.in_(target_map_ids)).all(),
    )
    if path_map is None:
        logger.error(
            f"Did not found path from {map_id} | {from_direction} to {target_map_ids} with waypoints {available_waypoints_ids}"
        )
    try:
        return path_map
    except ResponseValidationError as err:
        logger.error(err.errors())
        raise err


@router.get("/from_coordinate/", response_model=MapSchema)
def map_from_hud(
    zone_text: str,
    coordinates: list[str],
    from_map_id: int | None = None,
    session: Session = Depends(session_local),
):
    map = get_map_from_hud(
        session,
        zone_text,
        coordinates,
        session.get_one(Map, from_map_id) if from_map_id else None,
    )
    return map


@router.get("/{map_id}/near_map_allowing_havre/", response_model=MapSchema)
def near_map_allowing_havre(
    map_id: int,
    session: Session = Depends(session_local),
):
    map = get_near_map_allowing_havre(session, session.get_one(Map, map_id))
    return map


@router.put(
    "/map_direction/{map_direction_id}/confirm/", response_model=MapDirectionSchema
)
def confirm_map_direction(
    map_direction_id: int,
    to_map_id: int,
    session: Session = Depends(session_local),
):
    map_dir = session.get_one(MapDirection, map_direction_id)
    map_dir.to_map_id = to_map_id
    session.commit()
    return map_dir


@router.delete("/map_direction/{map_direction_id}")
def delete_map_direction(
    map_direction_id: int,
    session: Session = Depends(session_local),
):
    session.query(MapDirection).filter(MapDirection.id == map_direction_id).delete()
    session.commit()


@router.get("/{map_id}/map_direction/", response_model=list[MapDirectionSchema])
def get_map_directions(
    map_id: int,
    from_direction: FromDirection | None = None,
    session: Session = Depends(session_local),
):
    map_directions = get_neighbors(session, map_id, from_direction)
    return map_directions


@router.get("/limit_maps_sub_area/", response_model=list[MapSchema])
def limit_maps_sub_area(
    sub_area_ids: list[int],
    session: Session = Depends(session_local),
):
    maps = get_limit_maps_sub_area_id(session, sub_area_ids)
    return maps
