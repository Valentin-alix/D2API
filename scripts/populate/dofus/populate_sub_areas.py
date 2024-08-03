import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import D2O_SUB_AREA_PATH
from src.models.monster import Monster
from src.models.sub_area import SubArea, monster_sub_area_association


def init_sub_areas(session: Session, d2i_texts: dict):
    print("importing sub areas")
    if session.query(SubArea).first() is not None:
        return
    valid_monster_ids: list[int] = [elem[0] for elem in session.query(Monster.id).all()]
    with open(D2O_SUB_AREA_PATH, encoding="utf8") as sub_areas_file:
        sub_areas = json.load(sub_areas_file)
        sub_areas_entities: list[SubArea] = []
        sub_area_monster_associations: list[tuple[int, int]] = []
        for sub_area in tqdm(sub_areas):
            sub_area_entity = SubArea(
                id=sub_area["id"],
                area_id=sub_area["areaId"],
                name=d2i_texts.get(str(sub_area["nameId"])),
                level=sub_area["level"],
            )
            sub_areas_entities.append(sub_area_entity)

            for monster_id in sub_area["monsters"]:
                if monster_id not in valid_monster_ids:
                    continue
                sub_area_monster_associations.append((sub_area["id"], monster_id))

        session.add_all(sub_areas_entities)
        session.flush()
        session.execute(
            monster_sub_area_association.insert().values(sub_area_monster_associations)
        )
        session.commit()
