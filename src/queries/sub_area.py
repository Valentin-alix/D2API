import math
import random

from sqlalchemy import case, func
from sqlalchemy.orm import Session, aliased, joinedload

from EzreD2Shared.shared.enums import AreaEnum, JobEnum
from EzreD2Shared.shared.utils.debugger import timeit
from EzreD2Shared.shared.utils.randomizer import (
    RANGE_DURATION_ACTIVITY,
    multiply_offset,
)
from src.models.collectable import Collectable, CollectableMapInfo
from src.models.character import Character
from src.models.drop import Drop
from src.models.item import Item
from src.models.job import Job
from src.models.monster import Monster
from src.models.area import Area
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.models.sub_area import SubArea
from src.models.price import Price
from src.queries.monster import get_monster_res_filter_elem


def get_average_drop_value(session: Session, sub_area_id: int, server_id: int) -> float:
    return (
        session.query(
            func.avg(Price.average * (Drop.percentage / 100)),
        )
        .select_from(SubArea)
        .join(Monster, SubArea.monsters)
        .join(Drop, Drop.monster_id == Monster.id)
        .join(Item, Item.id == Drop.item_id)
        .join(Price, Price.item_id == Item.id)
        .filter(SubArea.id == sub_area_id, Price.server_id == server_id)
        .scalar()
    )


def get_dropable_items(session: Session, sub_area_id: int) -> list[Item]:
    return (
        session.query(Item)
        .join(Drop, Item.id == Drop.item_id)
        .join(Monster, Drop.monster_id == Monster.id)
        .join(SubArea, Monster.sub_areas)
        .filter(SubArea.id == sub_area_id)
        .all()
    )


def get_weights_fight_map(
    session: Session, server_id: int, valid_sub_areas: list[SubArea], lvl: int
) -> dict[int, float]:
    valid_sub_areas_ids: list[int] = [sub_area.id for sub_area in valid_sub_areas]

    weights: dict[int, float] = {}

    sub_area_with_drop_value = (
        session.query(
            SubArea,
            func.avg(Price.average * (Drop.percentage / 100)),
        )
        .select_from(SubArea)
        .join(Monster, SubArea.monsters)
        .join(Drop, Drop.monster_id == Monster.id)
        .join(Price, Price.item_id == Drop.item_id)
        .filter(SubArea.id.in_(valid_sub_areas_ids), Price.server_id == server_id)
        .group_by(SubArea.id)
        .options(joinedload(SubArea.maps))
        .all()
    )

    for sub_area, drop_value in sub_area_with_drop_value:
        sub_area: SubArea
        weight: float = drop_value
        if lvl < 200:
            weight *= sub_area.level
        for map in sub_area.maps:
            weights[map.id] = weight

    return weights


def get_max_time_fighter(session: Session, sub_areas: list[SubArea]) -> int:
    """get max time for farming subs area, it increase less and less from map count with log2

    Args:
        sub_area (SubArea)

    Returns:
        int: the max time to farming this sub area
    """

    count_maps = (
        session.query(Map)
        .filter(Map.sub_area_id.in_([elem.id for elem in sub_areas]))
        .count()
    )
    maps_time = min((300 + (count_maps * 100) / math.log2(count_maps)) * 2, 3600)
    return int(maps_time * multiply_offset(RANGE_DURATION_ACTIVITY))


STOP_LVL_SUB_AREA_FARM: dict[int, int] = {AreaEnum.INCARNAM: 15}


def get_valid_sub_areas_fighter(
    session: Session, character: Character
) -> list[SubArea]:
    """get valid sub areas for character based on lvl & sub zone

    Returns:
        list[SubArea]: valid sub areas
    """
    query = session.query(SubArea).filter(
        SubArea.is_farmable, SubArea.level <= character.lvl
    )
    if not character.is_sub:
        query = query.join(Area, SubArea.area_id == Area.id).filter(
            ~Area.is_for_sub,
        )

    stop_lvl_case = case(
        {area_id: max_lvl for area_id, max_lvl in STOP_LVL_SUB_AREA_FARM.items()},
        value=SubArea.area_id,
        else_=200,
    )

    valid_sub_areas = (
        query.join(Monster, SubArea.monsters)
        .filter(
            ~get_monster_res_filter_elem(character.elem),
            character.lvl <= stop_lvl_case,
        )
        .all()
    )

    return valid_sub_areas


STOP_JOB_LVL_AREA_FARM: dict[int, int] = {AreaEnum.INCARNAM: 20}


WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.ALCHIMIST: 5,
    JobEnum.WOODCUTTER: 10,
    JobEnum.PEASANT: 3,
    JobEnum.FISHERMAN: 3,
}


@timeit
def get_weights_harvest_map(
    session: Session,
    server_id: int,
    possible_collectables: list[Collectable],
    valid_sub_areas: list[SubArea],
) -> dict[int, float]:
    """get weight by all maps based on COLLECTABLE_BY_MAPS_WITH_COUNT and jobs_level

    Args:
        jobs_level (dict[Job, int]): a dict containing the lvl of the jobs

    Returns:
        dict[Map, float]: all weight by map
    """
    weight_maps: dict[int, float] = {}

    possible_collectables_ids: list[int] = [
        collectable.id for collectable in possible_collectables
    ]
    weight_by_job_case = case(
        *[(Job.name == job_name, weight) for job_name, weight in WEIGHT_BY_JOB.items()],
        else_=0,
    )
    valid_sub_areas_ids: list[int] = [sub_area.id for sub_area in valid_sub_areas]
    for map, map_collectables_value in (
        session.query(
            Map,
            func.sum(
                (Price.average * CollectableMapInfo.count * (Item.level / 20 + 1))
                * weight_by_job_case
            ),
        )
        .select_from(CollectableMapInfo)
        .join(Map, CollectableMapInfo.map_id == Map.id)
        .join(Collectable, Collectable.id == CollectableMapInfo.collectable_id)
        .join(Job, Job.id == Collectable.job_id)
        .join(Item, Item.id == Collectable.item_id)
        .join(Price, Item.id == Price.item_id)
        .join(SubArea, SubArea.id == Map.sub_area_id)
        .filter(
            Price.server_id == server_id,
            Collectable.id.in_(possible_collectables_ids),
            SubArea.id.in_(valid_sub_areas_ids),
        )
        .group_by(Map.id)
        .all()
    ):
        weight_maps[map.id] = max(map_collectables_value, 1)

    return weight_maps


def get_valid_sub_areas_harvester(
    session: Session, character: Character
) -> list[SubArea]:
    """get valid sub areas for character based on lvl & sub zone

    Returns:
        list[SubArea]: valid sub areas
    """
    if not character.is_sub:
        query = (
            session.query(SubArea)
            .join(Area, SubArea.area_id == Area.id)
            .filter(
                SubArea.is_farmable,
                SubArea.is_not_aggressive(character.lvl),
                ~Area.is_for_sub,
            )
        )
    else:
        query = session.query(SubArea).filter(
            SubArea.is_farmable,
            SubArea.is_not_aggressive(character.lvl),
        )

    min_harvest_job_lvl: int = min(
        (elem.lvl for elem in character.harvest_jobs_infos), default=1
    )

    stop_lvl_case = case(
        {area_id: max_lvl for area_id, max_lvl in STOP_JOB_LVL_AREA_FARM.items()},
        value=SubArea.area_id,
        else_=200,
    )

    return query.filter(min_harvest_job_lvl <= stop_lvl_case).all()


def get_max_time_harvester(session: Session, sub_areas: list[SubArea]) -> int:
    """get max time for farming subs area, it increase less and less from map count with log2

    Args:
        sub_area (SubArea)

    Returns:
        int: the max time to farming this sub area
    """

    count_maps = (
        session.query(Map)
        .filter(Map.sub_area_id.in_([elem.id for elem in sub_areas]))
        .count()
    )
    maps_time = min((300 + (count_maps * 100) / math.log2(count_maps)) * 0.6, 3600)
    return int(maps_time * multiply_offset(RANGE_DURATION_ACTIVITY))


def get_average_sub_area_weight(
    sub_area: SubArea, weights_by_map: dict[int, float], is_sub: bool
) -> float:
    count_maps = len(sub_area.maps)
    if count_maps == 0:
        return 0
    if not sub_area.area.is_for_sub and is_sub:
        return 0
    return sum(weights_by_map.get(map.id, 1) for map in sub_area.maps) / count_maps


def get_neighbor_sub_area(
    session: Session, sub_area_id: int, valid_sub_areas_ids: list[int]
) -> list["SubArea"]:
    ToMapAlias = aliased(Map)

    return (
        session.query(SubArea)
        .join(Map, Map.sub_area_id == SubArea.id)
        .join(MapDirection, MapDirection.from_map_id == Map.id)
        .join(ToMapAlias, ToMapAlias.id == MapDirection.to_map_id)
        .filter(
            SubArea.id.in_(valid_sub_areas_ids), ToMapAlias.sub_area_id == sub_area_id
        )
        .all()
    )


@timeit
def get_random_grouped_sub_area(
    session: Session,
    sub_area_ids_farming: list[int],
    weights_by_map: dict[int, float],
    valid_sub_area_ids: list[SubArea],
    is_sub: bool,
) -> list[SubArea]:
    count_min_sub_area = min(
        (sub_area_ids_farming.count(sub_area.id) for sub_area in valid_sub_area_ids),
        default=0,
    )
    less_farmed_sub_areas = [
        sub_area
        for sub_area in valid_sub_area_ids
        if sub_area_ids_farming.count(sub_area.id) == count_min_sub_area
    ]

    sub_area = random.choices(
        less_farmed_sub_areas,
        [
            get_average_sub_area_weight(sub_area, weights_by_map, is_sub)
            for sub_area in less_farmed_sub_areas
        ],
    )[0]
    neighbor_sub_area = get_neighbor_sub_area(
        session, sub_area.id, [elem.id for elem in valid_sub_area_ids]
    )
    return [sub_area] + neighbor_sub_area
