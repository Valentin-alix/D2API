import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import D2O_JOB_PATH
from src.models.job import Job


def init_job(session: Session, d2i_texts: dict):
    print("importing jobs...")
    if session.query(Job).first() is not None:
        return

    with open(D2O_JOB_PATH, encoding="utf8") as file:
        jobs = json.load(file)
        jobs_entities: list[Job] = []
        for job in tqdm(jobs):
            jobs_entities.append(
                Job(id=job["id"], name=d2i_texts.get(str(job["nameId"])))
            )
        session.add_all(jobs_entities)
        session.commit()
