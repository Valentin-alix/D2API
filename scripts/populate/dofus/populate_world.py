import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import D2O_WORLD_PATH
from src.models.world import World


def init_world(session: Session, d2i_texts: dict):
    print("importing worlds...")
    if session.query(World).first() is not None:
        return

    with open(D2O_WORLD_PATH, encoding="utf8") as file:
        worlds = json.load(file)
        world_entities: list[World] = []
        for world in tqdm(worlds):
            world_entities.append(
                World(id=world["id"], name=d2i_texts.get(str(world["nameId"])))
            )
        session.add_all(world_entities)
        session.commit()
