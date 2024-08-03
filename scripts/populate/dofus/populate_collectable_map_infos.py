import asyncio
import json
import os
from time import perf_counter

import aiohttp
from pydantic import BaseModel, RootModel
from sqlalchemy.orm import Session
from tqdm import tqdm

from D2Shared.shared.utils.clean import clean_item_name
from scripts.populate.dofus.consts import COLLECTABLES_MAP_PATH
from src.models.collectable import Collectable, CollectableMapInfo
from src.models.item import Item
from src.queries.map import get_related_map


class CollectableInfoMap(BaseModel):
    name: str
    count_by_map_id: list[tuple[int, int]] = []

    def __hash__(self) -> int:
        return self.name.__hash__()


class ListCollectablesMapCount(RootModel):
    root: set[CollectableInfoMap]


async def fetch_item_index_interactive_doflex(
    db_session: Session,
    session: aiohttp.ClientSession,
    index: int,
    lock: asyncio.Lock,
    maps_with_count: ListCollectablesMapCount,
):
    async def get_maps_with_count_by_result(
        session: Session,
        result: dict,
    ):
        if (name := result.get("name")) is not None:
            if (_map_infos := result.get("maps", [])) == []:
                return
            collectable_info_map = CollectableInfoMap(name=name)
            for _map_info in _map_infos:
                related_map = get_related_map(
                    session, x=_map_info["x"], y=_map_info["y"], world_id=_map_info["w"]
                )
                if related_map is None:
                    continue
                collectable_info_map.count_by_map_id.append(
                    (related_map.id, _map_info["n"])
                )
            async with lock:
                maps_with_count.root.add(collectable_info_map)

    async with session.get(
        f"https://doflex.fr/fr/encyclopedia/items/{index}/interactives.json"
    ) as result:
        if result.status == 200:
            result = await result.json()
            await get_maps_with_count_by_result(db_session, result)


async def fetch_multiple_item_index_interactive_doflex(
    db_session: Session,
    session: aiohttp.ClientSession,
    urls: range,
    lock: asyncio.Lock,
    maps_with_count: ListCollectablesMapCount,
):
    tasks: list[asyncio.Task] = []
    for url in urls:
        task = asyncio.create_task(
            fetch_item_index_interactive_doflex(
                db_session, session, url, lock, maps_with_count
            )
        )
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res


async def fetch_all_items_doflex(
    db_session: Session, lock: asyncio.Lock, maps_with_count: ListCollectablesMapCount
):
    step = 10
    for _range in tqdm(range(step, 20000, step)):
        urls = range(_range - step, _range)
        connector = aiohttp.TCPConnector(limit=10, force_close=True)
        async with aiohttp.ClientSession(
            connector=connector, timeout=aiohttp.ClientTimeout(total=None)
        ) as session:
            await fetch_multiple_item_index_interactive_doflex(
                db_session, session, urls, lock, maps_with_count
            )


async def get_map_collectables_info(db_session: Session) -> ListCollectablesMapCount:
    maps_with_count: ListCollectablesMapCount = ListCollectablesMapCount(root=set())
    lock = asyncio.Lock()
    if not os.path.exists(COLLECTABLES_MAP_PATH):
        before = perf_counter()
        await fetch_all_items_doflex(db_session, lock, maps_with_count)
        print(perf_counter() - before)
        with open(COLLECTABLES_MAP_PATH, "w+") as file:
            file.write(maps_with_count.model_dump_json())
    else:
        with open(COLLECTABLES_MAP_PATH, "r") as file:
            maps_with_count = ListCollectablesMapCount.model_validate(json.load(file))
    return maps_with_count


async def init_collectables_map_infos(session: Session):
    print("importing collectables map infos...")
    if session.query(CollectableMapInfo).first() is not None:
        return

    collectables_info = await get_map_collectables_info(session)

    collectables_infos_entities: list[CollectableMapInfo] = []

    item_id_by_name: dict[str, int] = {
        clean_item_name(elem[0]): elem[1]
        for elem in session.query(Item.name, Item.id).all()
    }
    collectable_by_item_id: dict[int, Collectable] = {
        _elem[0]: _elem[1]
        for _elem in session.query(Collectable.item_id, Collectable).all()
    }

    for map_collectable_info in tqdm(collectables_info.root):
        related_item_id: int = item_id_by_name[
            clean_item_name(map_collectable_info.name)
        ]
        related_collectable = collectable_by_item_id.get(related_item_id, None)
        if related_collectable is None:
            continue
        for map_id, count in map_collectable_info.count_by_map_id:
            collectables_infos_entities.append(
                CollectableMapInfo(
                    map_id=map_id, collectable_id=related_collectable.id, count=count
                )
            )
    session.add_all(collectables_infos_entities)
    session.commit()
