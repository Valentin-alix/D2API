from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.job import JobSchema
from src.database import session_local
from src.queries.job import find_job_by_text
from src.security.auth import login

router = APIRouter(prefix="/job", dependencies=[Depends(login)])


@router.get("/by_text/", response_model=JobSchema | None)
def job_by_text(
    text: str,
    session: Session = Depends(session_local),
):
    related_job = find_job_by_text(session, text)
    return related_job
