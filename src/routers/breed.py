from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.breed import BreedSchema
from src.database import session_local
from src.models.stats.breed import Breed

router = APIRouter(prefix="/breed")


@router.get("/", response_model=list[BreedSchema])
def get_breeds(
    session: Session = Depends(session_local),
):
    breeds = session.query(Breed).all()
    return breeds
