import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import (
    D2O_CHARACTERISTIC_CATEGORY_PATH,
    D2O_CHARACTERISTIC_PATH,
)
from src.models.characteristic import (
    Characteristic,
    CharacteristicCategory,
)


def init_characteristics(session: Session, d2i_texts: dict):
    print("importing characteristic categories...")
    if session.query(CharacteristicCategory).first() is not None:
        return

    with open(D2O_CHARACTERISTIC_CATEGORY_PATH, encoding="utf8") as file:
        char_categories = json.load(file)
        char_categories_entities: list[CharacteristicCategory] = []
        for char_category in tqdm(char_categories):
            char_categories_entities.append(
                CharacteristicCategory(
                    id=char_category["id"],
                    name=d2i_texts.get(str(char_category["nameId"])),
                )
            )

        print("importing characteristic...")
        with open(D2O_CHARACTERISTIC_PATH, encoding="utf8") as file:
            chars = json.load(file)
            char_entities: list[Characteristic] = []
            for char in tqdm(chars):
                related_category_id = next(
                    (
                        elem["id"]
                        for elem in char_categories
                        if char["id"] in elem["characteristicIds"]
                    ),
                    None,
                )
                char_entities.append(
                    Characteristic(
                        id=char["id"],
                        name=d2i_texts.get(str(char["nameId"])),
                        characteristic_category_id=related_category_id,
                    )
                )

        session.add_all(char_categories_entities)
        session.add_all(char_entities)
        session.commit()
