from sqlalchemy.orm import Session

from D2Shared.shared.utils.text_similarity import get_similarity
from src.models.job import Job


def find_job_by_text(session: Session, text: str) -> Job | None:
    jobs = session.query(Job).all()
    jobs_similarity = [
        (job, similarity)
        for job in jobs
        if (similarity := get_similarity(job.name, text)) > 0.6
    ]
    if len(jobs_similarity) == 0:
        return None
    return max(jobs_similarity, key=lambda elem: elem[1])[0]
