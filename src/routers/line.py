from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.stat import LineSchema
from src.database import session_local
from src.models.rune import Line
from src.security.auth import login

router = APIRouter(prefix="/line", dependencies=[Depends(login)])


@router.get("/{line_id}/", response_model=LineSchema)
def add_spent_quantity(
    line_id: int,
    spent_quantity: int,
    session: Session = Depends(session_local),
):
    line = session.get_one(Line, line_id)
    line.spent_quantity += spent_quantity
    return line
