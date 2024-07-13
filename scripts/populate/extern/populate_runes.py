import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from D2Shared.shared.utils.text_similarity import get_similarity
from scripts.populate.extern.consts import RUNES_JSON_PATH
from src.models.item import Item
from src.models.rune import Rune, Stat


def init_runes(session: Session):
    print("importing runes...")
    if session.query(Stat).first() is not None:
        return
    item_id_by_names = {elem.name: elem.id for elem in session.query(Item).all()}
    with open(RUNES_JSON_PATH, encoding="utf-8") as file:
        stats = json.load(file)
        stats_instance: list[Stat] = []
        runes_instance: list[Rune] = []
        for stat in tqdm(stats):
            stat_instance = Stat(name=stat["name"], weight=stat["weight"])
            stats_instance.append(stat_instance)
            for rune in stat["runes"]:
                most_sim_item_name = max(
                    item_id_by_names.keys(),
                    key=lambda _elem: get_similarity(_elem, rune["name"]),
                )
                runes_instance.append(
                    Rune(
                        stat_quantity=rune["quantity"],
                        name=rune["name"],
                        stat=stat_instance,
                        item_id=item_id_by_names[most_sim_item_name],
                    )
                )
    session.add_all(stats_instance)
    session.add_all(runes_instance)
    session.commit()
