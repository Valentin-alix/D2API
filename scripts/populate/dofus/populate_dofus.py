import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(Path(__file__).parent.parent.parent.parent))

from scripts.populate.dofus.consts import (
    D2I_PATH,
)
from scripts.populate.dofus.populate_areas import (
    init_areas,
)
from scripts.populate.dofus.populate_collectable_map_infos import (
    init_collectables_map_infos,
)
from scripts.populate.dofus.populate_drops import (
    init_monsters,
)
from scripts.populate.dofus.populate_icon import init_icons
from scripts.populate.dofus.populate_items import (
    init_item,
)
from scripts.populate.dofus.populate_jobs import init_job
from scripts.populate.dofus.populate_maps import (
    init_map,
)
from scripts.populate.dofus.populate_maps_directions import init_map_directions
from scripts.populate.dofus.populate_prices_servers import init_prices_and_servers
from scripts.populate.dofus.populate_recipes import (
    init_recipes,
)
from scripts.populate.dofus.populate_sub_areas import init_sub_areas
from scripts.populate.dofus.populate_type_item import init_type
from scripts.populate.dofus.populate_waypoint import init_waypoint
from scripts.populate.dofus.populate_world import init_world
from src.database import ENGINE, SessionMaker, run_migrations
from src.models.base import Base


async def init_bdd():
    run_migrations()

    Base.metadata.create_all(ENGINE)

    session = SessionMaker()

    with open(D2I_PATH, encoding="utf8") as d2i_file:
        d2i_texts = json.load(d2i_file)["texts"]
        init_icons(session)
        init_type(session, d2i_texts)
        init_item(session, d2i_texts)
        init_monsters(session, d2i_texts)
        init_areas(session, d2i_texts)
        init_sub_areas(session, d2i_texts)
        init_job(session, d2i_texts)
        init_recipes(session)
        init_world(session, d2i_texts)
        init_map(session)
        init_waypoint(session)
        init_map_directions(session)
        init_prices_and_servers(session)
        await init_collectables_map_infos(session)


if __name__ == "__main__":
    asyncio.run(init_bdd())
