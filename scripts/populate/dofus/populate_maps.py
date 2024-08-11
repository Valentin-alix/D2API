import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import (
    D2O_MAP_POS_PATH,
)
from src.models.map import Map
from src.models.sub_area import SubArea
from src.queries.map import get_related_neighbor_map
from src.queries.utils import get_auto_id


def init_default_directions(
    session: Session,
    map: Map,
    or_create: bool = True,
):
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
        init_default_directions(session, neighbor, False)

        return neighbor.id

    def get_top_map_id() -> int | None:
        return get_neighbor_map_id(0, -1)

    def get_bot_map_id():
        return get_neighbor_map_id(0, 1)

    def get_right_map_id():
        return get_neighbor_map_id(1, 0)

    def get_left_map_id():
        return get_neighbor_map_id(-1, 0)

    map.left_map_id = get_left_map_id()
    map.right_map_id = get_right_map_id()
    map.top_map_id = get_top_map_id()
    map.bot_map_id = get_bot_map_id()
    session.flush()


def init_map_directions(session: Session):
    print("importing maps directions...")
    for map in tqdm(session.query(Map).all()):
        init_default_directions(session, map)


def init_map(session: Session):
    CAPABILITY_ALLOW_TELEPORT_FROM: int = 8

    print("importing maps...")
    if session.query(Map).first() is not None:
        return

    sub_area_ids: list[int] = [elem[0] for elem in session.query(SubArea.id).all()]
    with open(D2O_MAP_POS_PATH, encoding="utf8") as file:
        maps_infos: list[dict] = json.load(file)
        maps_entities: list[Map] = []
        for map_info in tqdm(maps_infos):
            if map_info["worldMap"] == -1 or not map_info["outdoor"]:
                continue
            if map_info["subAreaId"] not in sub_area_ids:
                continue
            can_havre_sac = (
                map_info["capabilities"] & CAPABILITY_ALLOW_TELEPORT_FROM
            ) != 0

            base_map_charac = {
                "x": map_info["posX"],
                "y": map_info["posY"],
                "world_id": map_info["worldMap"],
                "sub_area_id": map_info["subAreaId"],
            }
            map = Map(
                id=int(map_info["id"]),
                **base_map_charac,
                can_havre_sac=can_havre_sac,
            )
            maps_entities.append(map)

        session.add_all(maps_entities)
        session.flush()
        init_map_directions(session)
        session.commit()
