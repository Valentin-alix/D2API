from sqlalchemy import case, func
from sqlalchemy.orm import Session

from src.models.collectable import Collectable
from src.models.config.character import Character, CharacterJobInfo
from src.models.items.item import Item
from src.models.job import Job


def populate_job_info(session: Session, character_id: str):
    """used at character creation"""
    job_infos: list[CharacterJobInfo] = []
    for job in session.query(Job).all():
        job_infos.append(CharacterJobInfo(job_id=job.id, character_id=character_id))
    session.add_all(job_infos)
    session.commit()


def get_possible_collectable(
    session: Session, harvest_jobs_infos: list[CharacterJobInfo]
) -> list[Collectable]:
    collectable_possible_lvl_case = case(
        {job_info.job_id: job_info.lvl for job_info in harvest_jobs_infos},
        value=Collectable.job_id,
        else_=200,
    )

    possible_collectables = (
        session.query(Collectable)
        .join(Item, Item.id == Collectable.item_id)
        .filter(
            Collectable.job_id.in_(
                [job_info.job_id for job_info in harvest_jobs_infos]
            ),
            Item.level <= collectable_possible_lvl_case,
        )
        .all()
    )

    return possible_collectables


def get_max_pods_character(session: Session, character_id: str) -> int:
    BASE_PODS = 1000

    levels_job_with_lvl = (
        session.query(func.sum(CharacterJobInfo.lvl), Character.lvl)
        .join(Character, Character.id == CharacterJobInfo.character_id)
        .filter(CharacterJobInfo.character_id == character_id)
        .group_by(Character.lvl)
        .one()
    )
    sum_job_lvls, lvl = levels_job_with_lvl
    bonus_pods = 0
    pod_by_lvl = 12
    for _ in range(200, sum_job_lvls, 200):
        bonus_pods += 200 * pod_by_lvl
        pod_by_lvl = max(pod_by_lvl - 1, 1)
    bonus_pods += (sum_job_lvls % 200) * pod_by_lvl

    return BASE_PODS + lvl * 5 + bonus_pods
