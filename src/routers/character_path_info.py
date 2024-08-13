from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.character_path_info import (
    CreateCharacterPathInfoSchema,
    ReadCharacterPathInfoSchema,
    UpdateCharacterPathInfoSchema,
)
from src.database import session_local
from src.models.character_path_info import CharacterPathInfo
from src.security.auth import login

router = APIRouter(prefix="/path_info", dependencies=[Depends(login)])


@router.post("/", response_model=ReadCharacterPathInfoSchema)
def create_path_info(
    path_info: CreateCharacterPathInfoSchema,
    session: Session = Depends(session_local),
):
    path_info_instance = CharacterPathInfo(
        character_id=path_info.character_id, name=path_info.name
    )
    session.add(path_info_instance)
    session.commit()
    return path_info_instance


@router.put("/{path_info_id}", response_model=ReadCharacterPathInfoSchema)
def update_path_info(
    path_info_id: int,
    path_info: UpdateCharacterPathInfoSchema,
    session: Session = Depends(session_local),
):
    path_info_instance = session.get_one(CharacterPathInfo, path_info_id)
    path_info_instance.name = path_info.name
    session.commit()
    return path_info_instance


@router.delete("/{path_info_id}")
def delete_path_info(
    path_info_id: int,
    session: Session = Depends(session_local),
):
    path_info_instance = session.get_one(CharacterPathInfo, path_info_id)
    session.delete(path_info_instance)
    session.commit()
