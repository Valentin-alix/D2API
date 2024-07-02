import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from D2Shared.shared.utils.clean import clean_item_name
from scripts.populate.dofus.collectable_init import get_map_collectables_info
from scripts.populate.dofus.consts import D2O_SKILL_PATH
from src.models.collectable import Collectable, CollectableMapInfo
from src.models.item import Item


async def init_collectables(session: Session):
    print("importing collectables...")
    session.query(CollectableMapInfo).delete()
    session.query(Collectable).delete()
    if session.query(Collectable).first() is not None:
        return

    collectables_info = await get_map_collectables_info(session)

    collectables_entities: list[Collectable] = []
    collectables_infos_entities: list[CollectableMapInfo] = []

    with open(D2O_SKILL_PATH, encoding="utf8") as d2o_skill_file:
        skills = json.load(d2o_skill_file)

        item_id_by_name: dict[str, int] = {
            clean_item_name(elem[0]): elem[1]
            for elem in session.query(Item.name, Item.id)
        }
        for map_collectable_info in tqdm(collectables_info.root):
            related_item_id: int = item_id_by_name[
                clean_item_name(map_collectable_info.name)
            ]
            related_job_id: int | None = next(
                (
                    skill["parentJobId"]
                    for skill in skills
                    if related_item_id == skill["gatheredRessourceItem"]
                ),
                None,
            )
            if related_job_id is None:
                continue

            collectable = Collectable(item_id=related_item_id, job_id=related_job_id)
            collectables_entities.append(collectable)

            for map_id, count in map_collectable_info.count_by_map_id:
                collectables_infos_entities.append(
                    CollectableMapInfo(
                        map_id=map_id, collectable=collectable, count=count
                    )
                )
    session.add_all(collectables_entities)
    session.add_all(collectables_infos_entities)
    session.commit()
