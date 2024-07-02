import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import RUNES_JSON_PATH
from src.models.rune import Rune, Stat


def init_runes(session: Session):
    print("importing runes...")
    if session.query(Stat).first() is not None:
        return
    with open(RUNES_JSON_PATH) as file:
        stats = json.load(file)
        stats_instance: list[Stat] = []
        runes_instance: list[Rune] = []
        for stat in tqdm(stats):
            stat_instance = Stat(name=stat["name"], weight=stat["weight"])
            stats_instance.append(stat_instance)
            for rune in stat["runes"]:
                runes_instance.append(
                    Rune(
                        quantity=rune["quantity"], name=rune["name"], stat=stat_instance
                    )
                )
    session.add_all(stats_instance)
    session.add_all(runes_instance)
    session.commit()
