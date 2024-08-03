import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import D2O_AREA_PATH
from src.models.area import Area


def init_areas(session: Session, d2i_texts: dict):
    print("importing areas")
    if session.query(Area).first() is not None:
        return
    with open(D2O_AREA_PATH, encoding="utf8") as areas_file:
        areas = json.load(areas_file)
        areas_entities = []
        for area in tqdm(areas):
            areas_entities.append(
                Area(id=area["id"], name=d2i_texts.get(str(area["nameId"])))
            )
        session.add_all(areas_entities)
        session.commit()
