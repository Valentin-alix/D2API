import asyncio
import json
import os
from time import perf_counter

import aiohttp
from pydantic import BaseModel, RootModel
from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.const import COLLECTABLES_MAP_PATH
from src.queries.map import get_related_map


class CollectableInfoMap(BaseModel):
    name: str
    count_by_map_id: list[tuple[int, int]] = []

    def __hash__(self) -> int:
        return self.name.__hash__()


class ListCollectablesMapCount(RootModel):
    root: set[CollectableInfoMap]


maps_with_count: ListCollectablesMapCount = ListCollectablesMapCount(root=set())
lock = asyncio.Lock()


async def fetch(db_session: Session, session: aiohttp.ClientSession, index: int):
    async with session.get(
        f"https://doflex.fr/fr/encyclopedia/items/{index}/interactives.json"
    ) as result:
        if result.status == 200:
            result = await result.json()
            await get_maps_with_count(db_session, result)


async def get_maps_with_count(
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


async def fetch_all(db_session, session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(db_session, session, url))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res


async def main(db_session: Session):
    step = 10
    for _range in tqdm(range(step, 20000, step)):
        urls = range(_range - (step - 1), _range)
        connector = aiohttp.TCPConnector(limit=10, force_close=True)
        async with aiohttp.ClientSession(
            connector=connector, timeout=aiohttp.ClientTimeout(total=None)
        ) as session:
            await fetch_all(db_session, session, urls)


async def get_map_collectables_info(db_session: Session) -> ListCollectablesMapCount:
    global maps_with_count
    if not os.path.exists(COLLECTABLES_MAP_PATH):
        before = perf_counter()
        await main(db_session)
        print(perf_counter() - before)
        with open(COLLECTABLES_MAP_PATH, "w+") as file:
            file.write(maps_with_count.model_dump_json())
    else:
        with open(COLLECTABLES_MAP_PATH, "r") as file:
            maps_with_count = ListCollectablesMapCount.model_validate(json.load(file))
    return maps_with_count
