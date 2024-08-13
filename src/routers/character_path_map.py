from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.character_path_map import (
    CreateUpdateCharacterPathMapSchema,
    ReadCharacterPathMapSchema,
)
from src.database import session_local
from src.models.character_path_map import CharacterPathMap
from src.queries.map import get_related_map
from src.security.auth import login

router = APIRouter(prefix="/path_map", dependencies=[Depends(login)])


@router.post("/", response_model=ReadCharacterPathMapSchema)
def create_path_map(
    path_map: CreateUpdateCharacterPathMapSchema,
    session: Session = Depends(session_local),
):
    related_map = get_related_map(
        session, path_map.map.x, path_map.map.y, path_map.map.world_id
    )
    path_map_instance = CharacterPathMap(
        character_path_info_id=path_map.character_path_info_id,
        order_index=path_map.order_index,
        map_id=related_map.id,
    )
    session.add(path_map_instance)
    session.commit()
    return path_map_instance


@router.put("/{path_map_id}", response_model=ReadCharacterPathMapSchema)
def update_path_map(
    path_map_id: int,
    path_map: CreateUpdateCharacterPathMapSchema,
    session: Session = Depends(session_local),
):
    related_path_map = session.get_one(CharacterPathMap, path_map_id)
    related_path_map.order_index = path_map.order_index
    related_path_map.map_id = get_related_map(
        session, path_map.map.x, path_map.map.y, path_map.map.world_id
    ).id
    session.commit()
    return related_path_map


@router.delete("/{path_map_id}")
def delete_path_map(
    path_map_id: int,
    session: Session = Depends(session_local),
):
    related_path_map = session.get_one(CharacterPathMap, path_map_id)
    session.delete(related_path_map)
    session.commit()
