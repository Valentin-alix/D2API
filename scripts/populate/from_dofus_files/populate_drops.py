import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.const import D2O_MONSTER_PATH
from src.models.drop import Drop
from src.models.items.item import Item
from src.models.monster import Monster


def init_monsters(session: Session, d2i_texts: dict):
    print("importing monsters & drops...")
    if session.query(Monster).first() is not None:
        return
    valid_item_ids: list[int] = [elem[0] for elem in session.query(Item.id).all()]
    with open(D2O_MONSTER_PATH, encoding="utf8") as file:
        monsters = json.load(file)
        monsters_entities: list[Monster] = []
        drop_entities: list[Drop] = []
        for monster in tqdm(monsters):
            grade = monster["grades"][0]
            monsters_entities.append(
                Monster(
                    id=monster["id"],
                    name=d2i_texts.get(str(monster["nameId"])),
                    earth_resistance=grade["earthResistance"],
                    air_resistance=grade["airResistance"],
                    fire_resistance=grade["fireResistance"],
                    water_resistance=grade["waterResistance"],
                )
            )
            for drop in monster["drops"]:
                if drop["hasCriteria"] is True:
                    continue
                if drop["objectId"] not in valid_item_ids:
                    continue
                drop_entities.append(
                    Drop(
                        id=drop["dropId"],
                        monster_id=drop["monsterId"],
                        item_id=drop["objectId"],
                        percentage=drop["percentDropForGrade1"],
                    )
                )

        session.add_all(monsters_entities)
        session.add_all(drop_entities)
        session.commit()
