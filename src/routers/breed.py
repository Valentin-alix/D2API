from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from EzreD2Shared.shared.schemas.breed import BreedSchema
from EzreD2Shared.shared.schemas.user import ReadUserSchema
from src.database import session_local
from src.models.stats.breed import Breed
from src.queries.auth import get_current_sub_user

router = APIRouter(prefix="/breed")


@router.get("/", response_model=list[BreedSchema])
def get_breeds(
    current_user: Annotated[ReadUserSchema, Depends(get_current_sub_user)],
    session: Session = Depends(session_local),
):
    breeds = session.query(Breed).all()
    return breeds
