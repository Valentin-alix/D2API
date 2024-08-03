import os

import cv2
import numpy
from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.dofus.consts import GFX_ICONS_ITEMS
from src.models.icon import Icon


def read_from_bytes(image_data: bytes) -> numpy.ndarray:
    np_arr = numpy.fromstring(image_data, numpy.uint8)  # type: ignore
    img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img_np


def init_icons(session: Session):
    print("importing icons...")
    if session.query(Icon).first() is not None:
        return

    icons_entities: list[Icon] = []
    for root, _, files in tqdm(os.walk(GFX_ICONS_ITEMS)):
        for file in files:
            if not file.endswith(".png") and not file.endswith(".jpg"):
                continue
            if not file[:-4].isnumeric():
                continue

            with open(os.path.join(root, file), "rb") as image_file:
                image_data = image_file.read()
                cv2_img = read_from_bytes(image_data)
                cv2_gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
                if cv2.countNonZero(cv2_gray) != 0:
                    icons_entities.append(Icon(id=file[:-4], image=image_data))

    session.add_all(icons_entities)
    session.commit()
