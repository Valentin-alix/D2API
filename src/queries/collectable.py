from sqlalchemy.orm import Session

from EzreD2Shared.shared.consts.object_configs import COLLECTABLE_CONFIG_BY_NAME
from EzreD2Shared.shared.entities.object_search_config import ObjectSearchConfig
from EzreD2Shared.shared.utils.clean import clean_item_name
from src.models.collectable import Collectable, CollectableMapInfo
from src.models.item import Item


def get_possible_collectables_configs_on_map(
    session: Session, map_id: int, possible_collectable_ids: list[int]
) -> list[ObjectSearchConfig]:
    collectable_names = (
        session.query(Item.name)
        .join(Collectable, Item.id == Collectable.item_id)
        .join(CollectableMapInfo, CollectableMapInfo.collectable_id == Collectable.id)
        .filter(
            Collectable.id.in_(possible_collectable_ids),
            CollectableMapInfo.map_id == map_id,
        )
        .all()
    )
    return [
        related_config
        for name in collectable_names
        if (related_config := COLLECTABLE_CONFIG_BY_NAME.get(clean_item_name(name[0])))
        is not None
    ]
