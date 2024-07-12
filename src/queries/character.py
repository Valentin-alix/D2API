from sqlalchemy import case
from sqlalchemy.orm import Session

from D2Shared.shared.consts.areas import FARMABLE_SUB_AREAS_BY_AREA
from src.models.area import Area
from src.models.character import Character, CharacterJobInfo
from src.models.collectable import Collectable
from src.models.item import Item
from src.models.job import Job
from src.models.sub_area import SubArea


def populate_job_info(session: Session, character_id: str):
    """used at character creation"""
    job_infos: list[CharacterJobInfo] = []
    for job in session.query(Job).all():
        job_infos.append(CharacterJobInfo(job_id=job.id, character_id=character_id))
    session.add_all(job_infos)
    session.commit()


def populate_sub_areas(session: Session, character: Character):
    """used at character creation"""
    farmable_sub_area_ids: list[int] = []
    for area_name, sub_area_names in FARMABLE_SUB_AREAS_BY_AREA.items():
        farmable_sub_area_ids.extend(
            [
                elem[0]
                for elem in session.query(SubArea.id)
                .join(Area, SubArea.area_id == Area.id)
                .filter(SubArea.name.in_(sub_area_names), Area.name == area_name)
                .all()
            ]
        )
    character.sub_areas = (
        session.query(SubArea).filter(SubArea.id.in_(farmable_sub_area_ids)).all()
    )
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
