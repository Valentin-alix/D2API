from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.job import JobSchema
from src.database import session_local
from src.queries.job import find_job_by_text

router = APIRouter(prefix="/job")


@router.get("/by_text/", response_model=JobSchema | None)
def job_by_text(
    text: str,
    session: Session = Depends(session_local),
):
    related_job = find_job_by_text(session, text)
    return related_job
