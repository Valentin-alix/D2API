from operator import and_, or_
from typing import Literal, overload

from sqlalchemy import func, literal
from sqlalchemy.orm import Session, aliased, joinedload, selectinload
from sqlalchemy.sql.base import ExecutableOption

from D2Shared.shared.enums import FromDirection
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.models.sub_area import SubArea
from src.models.world import World


def get_limit_maps_sub_area_id(session: Session, sub_area_ids: list[int]) -> list[Map]:
    ToMapAlias = aliased(Map)
    limit_maps_query = (
        session.query(Map)
        .join(SubArea, SubArea.id == Map.sub_area_id)
        .filter(SubArea.id.in_(sub_area_ids))
        .join(MapDirection, MapDirection.from_map_id == Map.id)
        .join(ToMapAlias, ToMapAlias.id == MapDirection.to_map_id)
    )

    limit_maps_query = limit_maps_query.filter(
        or_(
            ToMapAlias.sub_area_id.not_in(sub_area_ids),
            and_(Map.waypoint != None, Map.world_id != 2),  # noqa: E711
        )
    )

    return limit_maps_query.all()


def get_neighbors(
    session: Session, map_id: int, from_direction: FromDirection | None
) -> list[MapDirection]:
    if from_direction is not None:
        extra_filters = (MapDirection.from_direction == from_direction,)
    else:
        extra_filters = ()
    return (
        session.query(MapDirection)
        .filter(MapDirection.from_map_id == map_id, *extra_filters)
        .options(joinedload(MapDirection.to_map))
        .all()
    )


def get_near_map_allowing_havre(session: Session, map: Map) -> Map:
    near_map_allow_havre = (
        session.query(Map)
        .filter(Map.allow_teleport_from)
        .order_by(Map.get_dist_map(map))
        .first()
    )
    assert near_map_allow_havre is not None
    return near_map_allow_havre


def get_related_neighbor_map(
    session: Session,
    from_map: Map,
    x_neighbor: int,
    y_neighbor: int,
    options: ExecutableOption | None = None,
) -> Map | None:
    query = (
        session.query(Map)
        .filter(
            Map.x == x_neighbor, Map.y == y_neighbor, Map.world_id == from_map.world_id
        )
        .order_by(
            (Map.id == from_map.id).asc(),
            (Map.sub_area_id == from_map.sub_area_id).desc(),
            (
                Map.has_priority_on_world_map == from_map.has_priority_on_world_map
            ).desc(),
        )
    )
    if options is not None:
        query = query.options(options)
    return query.first()


def get_map_from_hud(
    session: Session, zone_text: str, coordinates: list[str], from_map: Map | None
) -> Map | None:
    world_id: int | None = (
        session.query(World.id)
        .filter(literal(zone_text).contains(func.lower(World.name)))
        .scalar()
    )
    if world_id is None:
        world_id = 1

    x, y = int(coordinates[0]), int(coordinates[1])
    if from_map is not None and world_id == from_map.world_id:
        map = get_related_neighbor_map(
            session, from_map, x, y, options=selectinload(Map.map_directions)
        )
        if map is None:
            return None
        return map

    map = get_related_map(
        session=session,
        x=x,
        y=y,
        world_id=world_id,
        options=selectinload(Map.map_directions),
        force=True,
    )

    return map


@overload
def get_related_map(
    session: Session,
    x: int,
    y: int,
    world_id: int,
    options: ExecutableOption | None = None,
    force: Literal[True] = ...,
) -> Map: ...


@overload
def get_related_map(
    session: Session,
    x: int,
    y: int,
    world_id: int,
    options: ExecutableOption | None = None,
    force: bool = False,
) -> Map | None: ...


def get_related_map(
    session: Session,
    x: int,
    y: int,
    world_id: int,
    options: ExecutableOption | None = None,
    force: bool = False,
) -> Map | None:
    query = (
        session.query(Map)
        .filter_by(x=x, y=y, world_id=world_id)
        .order_by(Map.has_priority_on_world_map.desc())
    )
    if options is not None:
        query = query.options(options)
    map = query.first()
    if force and not map:
        raise ValueError("related map can't be None")
    return map
