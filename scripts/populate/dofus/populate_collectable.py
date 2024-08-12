import json

from sqlalchemy.orm import Session

from scripts.populate.dofus.consts import D2O_SKILL_PATH
from src.models.collectable import Collectable


def init_collectables(session: Session):
    print("importing collectables...")
    if session.query(Collectable).first() is not None:
        return

    collectables: list[Collectable] = []
    with open(D2O_SKILL_PATH, encoding="utf8") as d2o_skill_file:
        skills = json.load(d2o_skill_file)

        for skill in skills:
            if skill["gatheredRessourceItem"] in [-1, 0]:
                continue
            if skill["gatheredRessourceItem"] in [
                _elem.item_id for _elem in collectables
            ]:
                continue
            collectables.append(
                Collectable(
                    item_id=skill["gatheredRessourceItem"], job_id=skill["parentJobId"]
                )
            )
    session.add_all(collectables)
    session.commit()
