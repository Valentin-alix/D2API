from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.stat import StatSchema
from src.database import session_local
from src.models.rune import Stat

router = APIRouter(prefix="/stat")


@router.get("/", response_model=list[StatSchema])
def get_stats(session: Session = Depends(session_local)):
    stats = session.query(Stat).all()
    return stats
