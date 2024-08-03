import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import D2O_WAYPOINT_PATH
from src.models.map import Map
from src.models.waypoint import Waypoint


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
