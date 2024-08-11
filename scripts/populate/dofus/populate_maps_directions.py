from tqdm import tqdm
from D2Shared.shared.enums import ToDirection
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.queries.map import get_related_neighbor_map
from src.queries.utils import get_auto_id


from sqlalchemy.orm import Session


def get_default_directions(
    session: Session,
    map: Map,
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
        get_default_directions(session, neighbor, False)

        return neighbor.id

    def get_top_map_id() -> int | None:
        return get_neighbor_map_id(0, -1)

    def get_bot_map_id():
        return get_neighbor_map_id(0, 1)

    def get_right_map_id():
        return get_neighbor_map_id(1, 0)

    def get_left_map_id():
        return get_neighbor_map_id(-1, 0)

    return [
        MapDirection(
            from_map_id=map.id, to_map_id=get_left_map_id(), direction=ToDirection.LEFT
        ),
        MapDirection(
            from_map_id=map.id,
            to_map_id=get_right_map_id(),
            direction=ToDirection.RIGHT,
        ),
        MapDirection(
            from_map_id=map.id, to_map_id=get_top_map_id(), direction=ToDirection.TOP
        ),
        MapDirection(
            from_map_id=map.id, to_map_id=get_bot_map_id(), direction=ToDirection.BOT
        ),
    ]


def init_map_directions(session: Session):
    print("importing maps directions...")
    if session.query(MapDirection).first():
        return
    map_directions: list[MapDirection] = []
    for map in tqdm(session.query(Map).all()):
        map_directions.extend(get_default_directions(session, map))
    session.add_all(map_directions)
    session.commit()
