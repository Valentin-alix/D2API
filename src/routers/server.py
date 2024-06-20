from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.server import ServerSchema
from src.database import session_local
from src.models.server import Server

router = APIRouter(prefix="/server")


@router.get("/", response_model=list[ServerSchema])
def get_servers(
    session: Session = Depends(session_local),
):
    servers = session.query(Server).all()
    return servers
