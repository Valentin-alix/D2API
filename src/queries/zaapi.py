from cachetools import cached
from cachetools.keys import hashkey
from sqlalchemy.orm import Session

from EzreD2Shared.shared.consts.maps import (
    BONTA_BANK_MAP_ID,
    BONTA_SALE_HOTEL_CONSUMABLE_MAP_ID,
    BONTA_SALE_HOTEL_RESOURCE_MAP_ID,
    BONTA_WORKSHOP_ALCHEMIST_MAP_ID,
    BONTA_WORKSHOP_FISHER_MAP_ID,
    BONTA_WORKSHOP_PEASANT_MAP_ID,
    BONTA_WORKSHOP_WOODCUTTER_MAP_ID,
    BONTA_ZAAP_MAP_ID,
)
from EzreD2Shared.shared.enums import CategoryZaapiEnum
from EzreD2Shared.shared.schemas.zaapi import ZaapiSchema
from src.models.navigations.map import Map


@cached(cache={})
def get_zaapis() -> dict[str, list[ZaapiSchema]]:
    zaapis: dict[str, list[ZaapiSchema]] = {
        "Bonta": [
            ZaapiSchema(
                category=CategoryZaapiEnum.VARIOUS,
                text="Banque",
                map_id=BONTA_BANK_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.VARIOUS,
                text="Zaap",
                map_id=BONTA_ZAAP_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des bûcherons",
                map_id=BONTA_WORKSHOP_WOODCUTTER_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des pêcheurs",
                map_id=BONTA_WORKSHOP_FISHER_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des alchimistes",
                map_id=BONTA_WORKSHOP_ALCHEMIST_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.WORKSHOP,
                text="Atelier des paysans",
                map_id=BONTA_WORKSHOP_PEASANT_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.SALE_HOTEL,
                text="Hôtel de vente des ressources",
                map_id=BONTA_SALE_HOTEL_RESOURCE_MAP_ID,
            ),
            ZaapiSchema(
                category=CategoryZaapiEnum.SALE_HOTEL,
                text="Hôtel de vente des consommables",
                map_id=BONTA_SALE_HOTEL_CONSUMABLE_MAP_ID,
            ),
        ]
    }
    return zaapis


@cached(cache={}, key=lambda _: hashkey())
def get_zaapis_by_zone(session: Session) -> dict[str, dict[Map, ZaapiSchema]]:
    zaapis_by_zone: dict[str, dict[Map, ZaapiSchema]] = {}
    for name, zaapis_schema in get_zaapis().items():
        zaapis = {session.get_one(Map, elem.map_id): elem for elem in zaapis_schema}
        zaapis_by_zone[name] = zaapis
    return zaapis_by_zone
