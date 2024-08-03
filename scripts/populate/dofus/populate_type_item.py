import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from D2Shared.shared.enums import CategoryEnum
from scripts.populate.dofus.consts import D2O_TYPE_ITEM_PATH
from src.models.type_item import TypeItem


def init_type(session: Session, d2i_texts: dict):
    print("importing types")
    if session.query(TypeItem).first() is not None:
        return
    with open(D2O_TYPE_ITEM_PATH, encoding="utf8") as d2o_type_file:
        type_items = json.load(d2o_type_file)
        type_items_entities = []
        for _type in tqdm(type_items):
            type_items_entities.append(
                TypeItem(
                    id=_type["id"],
                    name=d2i_texts.get(str(_type["nameId"])),
                    category=CategoryEnum(_type["categoryId"]),
                )
            )
        session.add_all(type_items_entities)
        session.commit()
