import json

from sqlalchemy.orm import Session, joinedload
from tqdm import tqdm

from EzreD2Shared.shared.enums import FromDirection, ToDirection
from scripts.populate.const import (
    D2O_MAP_POS_PATH,
    D2O_WAYPOINT_PATH,
    D2O_WORLD_PATH,
)
from src.models.navigations.map import Map
from src.models.navigations.map_direction import (
    MapDirection,
)
from src.models.navigations.sub_area import SubArea
from src.models.navigations.waypoint import Waypoint
from src.models.navigations.world import World
from src.queries.map import get_related_neighbor_map
from src.queries.utils import get_auto_id
from src.queries.zaapi import get_zaapis


def init_world(session: Session, d2i_texts: dict):
    print("importing worlds...")
    if session.query(World).first() is not None:
        return

    with open(D2O_WORLD_PATH, encoding="utf8") as file:
        worlds = json.load(file)
        world_entities: list[World] = []
        for world in tqdm(worlds):
            world_entities.append(
                World(id=world["id"], name=d2i_texts.get(str(world["nameId"])))
            )
        session.add_all(world_entities)
        session.commit()


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


def init_map(session: Session):
    CAPABILITY_ALLOW_TELEPORT_FROM: int = 8
    CAPABILITY_ALLOW_MONSTER_FIGHT: int = 16384

    print("importing maps...")
    sub_area_ids: list[int] = [elem[0] for elem in session.query(SubArea.id).all()]
    if session.query(Map).first() is not None:
        return

    with open(D2O_MAP_POS_PATH, encoding="utf8") as file:
        maps_infos: list[dict] = json.load(file)
        maps_entities: list[Map] = []
        for map_info in tqdm(maps_infos):
            if map_info["worldMap"] == -1 or not map_info["outdoor"]:
                continue
            if map_info["subAreaId"] not in sub_area_ids:
                continue
            allow_teleport_from = (
                map_info["capabilities"] & CAPABILITY_ALLOW_TELEPORT_FROM
            ) != 0
            allow_monster_fight = (
                map_info["capabilities"] & CAPABILITY_ALLOW_MONSTER_FIGHT
            ) != 0

            base_map_charac = {
                "x": map_info["posX"],
                "y": map_info["posY"],
                "world_id": map_info["worldMap"],
                "sub_area_id": map_info["subAreaId"],
                "has_priority_on_world_map": map_info["hasPriorityOnWorldmap"],
            }
            map = Map(
                id=int(map_info["id"]),
                **base_map_charac,
                allow_teleport_from=allow_teleport_from,
                allow_monster_fight=allow_monster_fight,
            )
            maps_entities.append(map)

        session.add_all(maps_entities)
        session.commit()


def init_map_directions(session: Session):
    print("importing maps directions...")

    if session.query(MapDirection).first() is not None:
        return

    maps_direction: list[MapDirection] = []

    zaapis_map_ids: list[int] = [
        zaapi.map_id for zaapis in get_zaapis().values() for zaapi in zaapis
    ]

    for map in tqdm(session.query(Map).options(joinedload(Map.waypoint)).all()):
        maps_direction.extend(
            get_defaults_directions(session, map, zaapis_map_id=zaapis_map_ids)
        )
    session.add_all(maps_direction)
    session.commit()


def init_waypoint(session: Session):
    print("importing waypoints...")
    if session.query(Waypoint).first() is not None:
        return

    valid_map_ids: list[int] = [elem[0] for elem in session.query(Map.id).all()]
    with open(D2O_WAYPOINT_PATH, encoding="utf8") as file:
        waypoints = json.load(file)
        waypoint_entities: list[Waypoint] = []
        for waypoint in tqdm(waypoints):
            if not waypoint["activated"]:
                continue
            if waypoint["mapId"] not in valid_map_ids:
                continue
            waypoint_entities.append(
                Waypoint(id=waypoint["id"], map_id=waypoint["mapId"])
            )
        session.add_all(waypoint_entities)
        session.commit()
