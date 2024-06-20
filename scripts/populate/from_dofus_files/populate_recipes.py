import json

from sqlalchemy.orm import Session
from tqdm import tqdm

from scripts.populate.const import D2O_RECIPE_PATH, D2O_SKILL_PATH
from src.models.ingredient import Ingredient
from src.models.recipe import Recipe


def init_recipes(session: Session):
    print("importing recipes")
    if session.query(Recipe).first() is not None:
        return

    with open(D2O_RECIPE_PATH, encoding="utf8") as d2o_recipe_file, open(
        D2O_SKILL_PATH, encoding="utf8"
    ) as d2o_skill_file:
        recipes = json.load(d2o_recipe_file)
        skills = json.load(d2o_skill_file)
        recipes_entities = []
        ingredients_entities = []
        for recipe in tqdm(recipes):
            related_job_id: int = next(
                skill["parentJobId"]
                for skill in skills
                if recipe["resultId"] in skill["craftableItemIds"]
            )
            recipe_entity = Recipe(
                result_item_id=recipe["resultId"], job_id=related_job_id
            )
            recipes_entities.append(recipe_entity)
            ingredients_entities.extend(
                Ingredient(
                    item_id=ingredient[0],
                    quantity=ingredient[1],
                    recipe=recipe_entity,
                )
                for ingredient in zip(recipe["ingredientIds"], recipe["quantities"])
            )

        session.add_all(recipes_entities)
        session.add_all(ingredients_entities)
        session.commit()
