from sqlalchemy.orm import Session, joinedload
from tqdm import tqdm

from D2Shared.shared.enums import FromDirection, ToDirection
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.queries.map import get_related_map, get_related_neighbor_map
from src.queries.utils import get_auto_id
from src.queries.zaapi import get_zaapis


def get_defaults_directions(
    session: Session,
    map: Map,
    zaapis_map_id: list[int],
    or_create: bool = True,
) -> list[MapDirection]:
    def get_neighbor_map_id(x_increment: int, y_increment: int) -> int | None:
        neighbor = get_related_neighbor_map(
            session, map, map.x + x_increment, map.y + y_increment
        )
        if not or_create or neighbor:
            return neighbor.id if neighbor else None

        neighbor = Map(
            id=get_auto_id(session, Map),
            x=map.x + x_increment,
            y=map.y + y_increment,
            sub_area_id=map.sub_area_id,
            world_id=map.world_id,
        )
        session.add(neighbor)
        session.flush()
        get_defaults_directions(session, neighbor, zaapis_map_id, False)

        return neighbor.id

    def get_top_map_id() -> int | None:
        return get_neighbor_map_id(0, -1)

    def get_bot_map_id():
        return get_neighbor_map_id(0, 1)

    def get_right_map_id():
        return get_neighbor_map_id(1, 0)

    def get_left_map_id():
        return get_neighbor_map_id(-1, 0)

    top_map_id = get_top_map_id()
    bot_map_id = get_bot_map_id()
    right_map_id = get_right_map_id()
    left_map_id = get_left_map_id()

    def get_default_map_by_direction(direction: ToDirection) -> int | None:
        if direction in [ToDirection.TOP_LEFT, ToDirection.TOP, ToDirection.TOP_RIGHT]:
            return top_map_id
        elif direction in [
            ToDirection.BOT_LEFT,
            ToDirection.BOT,
            ToDirection.BOT_RIGHT,
        ]:
            return bot_map_id
        elif direction in [
            ToDirection.RIGHT_TOP,
            ToDirection.RIGHT,
            ToDirection.RIGHT_BOT,
        ]:
            return right_map_id
        elif direction in [
            ToDirection.LEFT_TOP,
            ToDirection.LEFT,
            ToDirection.LEFT_BOT,
        ]:
            return left_map_id

    new_map_directions: list[MapDirection] = []
    for from_direction in FromDirection:
        for to_direction in ToDirection:
            if from_direction == FromDirection.WAYPOINT and map.waypoint is None:
                continue
            if from_direction == FromDirection.ZAAPI and map.id not in zaapis_map_id:
                continue
            to_map_id = get_default_map_by_direction(to_direction)
            if to_map_id is None:
                continue
            new_map_directions.append(
                MapDirection(
                    from_direction=from_direction,
                    to_direction=to_direction,
                    from_map_id=map.id,
                    to_map_id=to_map_id,
                )
            )
    return new_map_directions


def init_map_directions(session: Session):
    print("importing maps directions...")

    if session.query(MapDirection).first() is not None:
        return

    maps_direction: list[MapDirection] = []

    zaapis_map_ids: list[int] = [
        get_related_map(
            session,
            x=zaapi.map_coordinates.x,
            y=zaapi.map_coordinates.y,
            world_id=zaapi.map_coordinates.world_id,
            force=True,
        ).id
        for zaapis in get_zaapis().values()
        for zaapi in zaapis
    ]

    for map in tqdm(session.query(Map).options(joinedload(Map.waypoint)).all()):
        maps_direction.extend(
            get_defaults_directions(session, map, zaapis_map_id=zaapis_map_ids)
        )
    session.add_all(maps_direction)
    session.commit()
