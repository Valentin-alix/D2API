from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.enums import FromDirection
from EzreD2Shared.shared.schemas.map import MapSchema
from EzreD2Shared.shared.schemas.map_direction import MapDirectionSchema
from EzreD2Shared.shared.schemas.map_with_action import MapWithActionSchema
from src.database import session_local
from src.models.navigations.map import Map
from src.models.navigations.map_direction import MapDirection
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


@router.get("/{map_id}", response_model=MapSchema)
def map(
    map_id: int,
    session: Session = Depends(session_local),
):
    return session.get_one(Map, map_id)


@router.get("/related/", response_model=MapSchema)
def related_map(
    x: int,
    y: int,
    world_id: int,
    session: Session = Depends(session_local),
):
    return get_related_map(session, x=x, y=y, world_id=world_id)


@router.get("/find_path/", response_model=list[MapWithActionSchema] | None)
def find_path(
    is_sub: bool,
    use_transport: bool,
    map_id: int,
    from_direction: FromDirection,
    available_waypoints_ids: list[int],
    target_map_ids: list[int],
    session: Session = Depends(session_local),
):
    astar_map = AstarMap(is_sub, use_transport, available_waypoints_ids, session)
    iter_path_map = astar_map.find_path(
        session.get_one(Map, map_id),
        from_direction,
        session.query(Map).filter(Map.id.in_(target_map_ids)).all(),
    )
    if iter_path_map is None:
        return None
    path_map = list(iter_path_map)
    return path_map


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
    map_dir.was_checked = True
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
    is_sub: bool,
    session: Session = Depends(session_local),
):
    maps = get_limit_maps_sub_area_id(session, sub_area_ids, is_sub)
    return maps
