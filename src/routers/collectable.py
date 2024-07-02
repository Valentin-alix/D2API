from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from src.database import session_local
from src.queries.collectable import get_possible_collectables_configs_on_map
from src.security.auth import login

router = APIRouter(prefix="/collectable", dependencies=[Depends(login)])


@router.get("/possible_on_map/", response_model=list[ObjectSearchConfig])
def possible_on_map(
    map_id: int,
    possible_collectable_ids: list[int],
    session: Session = Depends(session_local),
):
    return get_possible_collectables_configs_on_map(
        session, map_id, possible_collectable_ids
    )
