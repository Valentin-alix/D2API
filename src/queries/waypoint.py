from sqlalchemy.orm import Session

from src.models.map import Map
from src.models.waypoint import Waypoint


def get_waypoints_by_world(session: Session, world_id: int) -> list[Waypoint]:
    return (
        session.query(Waypoint)
        .join(Map, Waypoint.map_id == Map.id)
        .filter(Map.world_id == world_id)
        .all()
    )
