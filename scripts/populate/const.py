import os
from pathlib import Path

PYDOFUS_OUTPUT_FOLDER = os.path.join(
    Path(__file__).parent.parent.parent, "PyDofus", "output"
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
D2O_BREED_PATH = os.path.join(D2O_FOLDER, "Breeds.json")
D2O_SPELL_VARIANT_PATH = os.path.join(D2O_FOLDER, "SpellVariants.json")
D2O_SPELLS_PATH = os.path.join(D2O_FOLDER, "Spells.json")
D2O_SPELL_LEVELS_PATH = os.path.join(D2O_FOLDER, "SpellLevels.json")
D2O_CHARACTERISTIC_CATEGORY_PATH = os.path.join(
    D2O_FOLDER, "CharacteristicCategories.json"
)
D2O_CHARACTERISTIC_PATH = os.path.join(D2O_FOLDER, "Characteristics.json")
D2O_EFFECTS_PATH = os.path.join(D2O_FOLDER, "Effects.json")
D2O_SPELL_STATE_PATH = os.path.join(D2O_FOLDER, "SpellStates.json")
D2O_MONSTER_PATH = os.path.join(D2O_FOLDER, "Monsters.json")

GFX_ICONS_ITEMS = os.path.join(PYDOFUS_OUTPUT_FOLDER, "gfx", "items")

D2I_PATH = os.path.join(PYDOFUS_OUTPUT_FOLDER, "d2i.json")

DLM_FOLDER = os.path.join(PYDOFUS_OUTPUT_FOLDER, "dlm")

AVG_PRICES_FOLDER = os.path.join(PYDOFUS_OUTPUT_FOLDER, "dat")

RUNES_JSON_PATH = os.path.join(
    Path(__file__).parent.parent.parent, "resources", "runes.json"
)
COLLECTABLES_MAP_PATH = os.path.join(
    Path(__file__).parent.parent.parent, "resources", "collectables.json"
)
