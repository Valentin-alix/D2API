from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.waypoint import WaypointSchema
from src.database import session_local
from src.queries.waypoint import get_waypoints_by_world
from src.security.auth import login

router = APIRouter(prefix="/world", dependencies=[Depends(login)])


@router.get("/{world_id}/waypoints", response_model=list[WaypointSchema])
def get_waypoints(
    world_id: int,
    session: Session = Depends(session_local),
):
    return get_waypoints_by_world(session, world_id)
