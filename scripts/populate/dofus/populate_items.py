import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import (
    D2O_ITEM_PATH,
)
from src.models.icon import Icon
from src.models.item import Item


def init_item(session: Session, d2i_texts: dict):
    print("importing item")
    if session.query(Item).first() is not None:
        return

    with open(D2O_ITEM_PATH, encoding="utf8") as d2o_item_file:
        items = json.load(d2o_item_file)
        items_entities = []
        valid_icon_ids: list[int] = [elem[0] for elem in session.query(Icon.id).all()]
        for item in tqdm(items):
            item_object = Item(
                id=item["id"],
                name=d2i_texts.get(str(item["nameId"])),
                type_item_id=item["typeId"],
                level=item["level"],
                is_saleable=item["isSaleable"],
                weight=item["realWeight"],
                icon_id=item["iconId"] if item["iconId"] in valid_icon_ids else None,
            )
            items_entities.append(item_object)
        session.add_all(items_entities)
        session.commit()
