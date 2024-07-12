from cachetools import cached
from cachetools.keys import hashkey
from sqlalchemy.orm import Session

from D2Shared.shared.consts.maps import (
    BONTA_BANK_MAP_CN,
    BONTA_SALE_HOTEL_CONSUMABLE_MAP_CN,
    BONTA_SALE_HOTEL_RESOURCE_MAP_CN,
    BONTA_WORKSHOP_ALCHEMIST_MAP_CN,
    BONTA_WORKSHOP_FISHER_MAP_CN,
    BONTA_WORKSHOP_PEASANT_MAP_CN,
    BONTA_WORKSHOP_WOODCUTTER_MAP_CN,
    BONTA_ZAAP_MAP_CN,
)
from D2Shared.shared.enums import CategoryZaapiEnum
from D2Shared.shared.schemas.zaapi import ZaapiSchema
from src.models.map import Map
from src.queries.map import get_related_map


@cached(cache={})
def get_zaapis() -> dict[str, list[ZaapiSchema]]:
    zaapis: dict[str, list[ZaapiSchema]] = {
        "Bonta": [
            ZaapiSchema(
                category=CategoryZaapiEnum.VARIOUS,
                text="Banque",
                map_coordinates=BONTA_BANK_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.VARIOUS,
                text="Zaap",
                map_coordinates=BONTA_ZAAP_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des bûcherons",
                map_coordinates=BONTA_WORKSHOP_WOODCUTTER_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des pêcheurs",
                map_coordinates=BONTA_WORKSHOP_FISHER_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des alchimistes",
                map_coordinates=BONTA_WORKSHOP_ALCHEMIST_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des paysans",
                map_coordinates=BONTA_WORKSHOP_PEASANT_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.SALE_HOTEL,
                text="Hôtel de vente des ressources",
                map_coordinates=BONTA_SALE_HOTEL_RESOURCE_MAP_CN,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.SALE_HOTEL,
                text="Hôtel de vente des consommables",
                map_coordinates=BONTA_SALE_HOTEL_CONSUMABLE_MAP_CN,
            ),
        ]
    }
    return zaapis


@cached(cache={}, key=lambda _: hashkey())
def get_zaapis_by_zone(session: Session) -> dict[str, dict[Map, ZaapiSchema]]:
    zaapis_by_zone: dict[str, dict[Map, ZaapiSchema]] = {}
    for name, zaapis_schema in get_zaapis().items():
        zaapis = {
            get_related_map(
                session,
                x=elem.map_coordinates.x,
                y=elem.map_coordinates.y,
                world_id=elem.map_coordinates.world_id,
                force=True,
            ): elem
            for elem in zaapis_schema
        }
        zaapis_by_zone[name] = zaapis
    return zaapis_by_zone
