import os
from pathlib import Path

PYDOFUS_OUTPUT_FOLDER = os.path.join(
    Path(__file__).parent.parent.parent.parent, "PyDofus", "output"
)

D2O_FOLDER = os.path.join(PYDOFUS_OUTPUT_FOLDER, "d2o")

D2O_ITEM_PATH = os.path.join(D2O_FOLDER, "Items.json")
D2O_TYPE_ITEM_PATH = os.path.join(D2O_FOLDER, "ItemTypes.json")
D2O_SUB_AREA_PATH = os.path.join(D2O_FOLDER, "SubAreas.json")
D2O_RECIPE_PATH = os.path.join(D2O_FOLDER, "Recipes.json")
D2O_WORLD_PATH = os.path.join(D2O_FOLDER, "WorldMaps.json")
D2O_MAP_POS_PATH = os.path.join(D2O_FOLDER, "MapPositions.json")
D2O_MAP_SCROLL_PATH = os.path.join(D2O_FOLDER, "MapScrollActions.json")
D2O_WAYPOINT_PATH = os.path.join(D2O_FOLDER, "Waypoints.json")
D2O_JOB_PATH = os.path.join(D2O_FOLDER, "Jobs.json")
D2O_SKILL_PATH = os.path.join(D2O_FOLDER, "Skills.json")
D2O_AREA_PATH = os.path.join(D2O_FOLDER, "Areas.json")
D2O_MONSTER_PATH = os.path.join(D2O_FOLDER, "Monsters.json")

GFX_ICONS_ITEMS = os.path.join(PYDOFUS_OUTPUT_FOLDER, "gfx", "items")

D2I_PATH = os.path.join(PYDOFUS_OUTPUT_FOLDER, "d2i.json")

DLM_FOLDER = os.path.join(PYDOFUS_OUTPUT_FOLDER, "dlm")

AVG_PRICES_FOLDER = os.path.join(PYDOFUS_OUTPUT_FOLDER, "dat")

COLLECTABLES_MAP_PATH = os.path.join(
    Path(__file__).parent.parent.parent.parent, "resources", "collectables.json"
)
