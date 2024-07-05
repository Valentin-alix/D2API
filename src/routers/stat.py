from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.stat import StatSchema
from src.database import session_local
from src.models.rune import Stat
from src.security.auth import login

router = APIRouter(prefix="/stat", dependencies=[Depends(login)])


@router.get("/", response_model=list[StatSchema])
def get_stats(session: Session = Depends(session_local)):
    stats = session.query(Stat).all()
    return stats
