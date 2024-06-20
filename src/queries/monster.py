from sqlalchemy import ColumnElement

from EzreD2Shared.shared.enums import ElemEnum
from src.models.monster import Monster


def get_monster_res_filter_elem(elem: ElemEnum) -> ColumnElement[bool]:
    THRESHOLD = 80

    match elem:
        case ElemEnum.ELEMENT_AIR:
            filter_elem = Monster.air_resistance > THRESHOLD
        case ElemEnum.ELEMENT_FIRE:
            filter_elem = Monster.fire_resistance > THRESHOLD
        case ElemEnum.ELEMENT_WATER:
            filter_elem = Monster.water_resistance > THRESHOLD
        case ElemEnum.ELEMENT_EARTH:
            filter_elem = Monster.earth_resistance > THRESHOLD
        case _:
            raise ValueError("Elem not valid.")

    return filter_elem
