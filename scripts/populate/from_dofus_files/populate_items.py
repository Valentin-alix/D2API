import json
import os

from sqlalchemy.orm import Session
from tqdm import tqdm

from EzreD2Shared.shared.enums import CategoryEnum
from scripts.populate.const import (
    AVG_PRICES_FOLDER,
    D2O_ITEM_PATH,
    D2O_TYPE_ITEM_PATH,
)
from src.models.icon import Icon
from src.models.item import Item
from src.models.type_item import TypeItem
from src.models.price import Price
from src.models.server import Server


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


def init_prices_and_servers(session: Session):
    print("importing prices & servers")
    if session.query(Price).first() is not None:
        return
    valid_items_ids: list[int] = [elem[0] for elem in session.query(Item.id).all()]
    prices: list[Price] = []
    servers: list[Server] = []
    for filename in os.listdir(AVG_PRICES_FOLDER):
        if not filename.endswith(".json"):
            continue
        print(f"importing prices for server {filename}")
        with open(os.path.join(AVG_PRICES_FOLDER, filename), encoding="utf8") as file:
            server = Server(name=filename[:-5])
            servers.append(server)
            item_by_price: dict[str, int] = json.load(file)
            for item_id, avg_price in tqdm(item_by_price.items()):
                if int(item_id) not in valid_items_ids:
                    continue
                prices.append(
                    Price(item_id=int(item_id), server=server, average=avg_price)
                )
    session.add_all(servers)
    session.add_all(prices)
    session.commit()
