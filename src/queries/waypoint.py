from cachetools import cached
from cachetools.keys import hashkey
from sqlalchemy.orm import Session

from src.models.map import Map
from src.models.waypoint import Waypoint


@cached(cache={}, key=lambda _, world_id: hashkey(world_id))
def get_waypoints_by_world(session: Session, world_id: int) -> list[Waypoint]:
    return (
        session.query(Waypoint)
        .join(Map, Waypoint.map_id == Map.id)
        .filter(Map.world_id == world_id)
        .all()
    )
