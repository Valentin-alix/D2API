import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import (
    D2O_MAP_POS_PATH,
)
from src.models.map import Map
from src.models.sub_area import SubArea


def init_map(session: Session):
    CAPABILITY_ALLOW_TELEPORT_FROM: int = 8

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
            )
            maps_entities.append(map)

        session.add_all(maps_entities)
        session.commit()
