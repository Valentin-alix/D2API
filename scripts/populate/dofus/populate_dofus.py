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
    init_sub_areas,
)
from scripts.populate.dofus.populate_characteristic import (
    init_characteristics,
)
from scripts.populate.dofus.populate_collectable import (
    init_collectables,
)
from scripts.populate.dofus.populate_drops import (
    init_monsters,
)
from scripts.populate.dofus.populate_icon import init_icons
from scripts.populate.dofus.populate_items import (
    init_item,
    init_prices_and_servers,
    init_type,
)
from scripts.populate.dofus.populate_jobs import init_job
from scripts.populate.dofus.populate_maps import (
    init_map,
    init_map_directions,
    init_waypoint,
    init_world,
)
from scripts.populate.dofus.populate_recipes import (
    init_recipes,
)
from scripts.populate.dofus.populate_spells import (
    init_breed,
    init_effects_spell,
    init_spell_levels,
    init_spell_lvl_index,
    init_spells_and_variant,
)
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
        init_characteristics(session, d2i_texts)
        init_breed(session, d2i_texts)
        init_effects_spell(session, d2i_texts)
        init_spells_and_variant(session, d2i_texts)
        init_spell_levels(session)
        init_spell_lvl_index(session)
        init_prices_and_servers(session)
        await init_collectables(session)


if __name__ == "__main__":
    asyncio.run(init_bdd())
