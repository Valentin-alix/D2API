import json
import os

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import AVG_PRICES_FOLDER
from src.models.item import Item
from src.models.price import Price
from src.models.server import Server


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
