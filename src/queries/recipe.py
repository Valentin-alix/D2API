from sqlalchemy import Row, func
from sqlalchemy.orm import Session, aliased, joinedload

from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.utils.debugger import timeit
from src.models.config.character import Character
from src.models.ingredient import Ingredient
from src.models.items.item import Item
from src.models.items.type_item import TypeItem
from src.models.price import Price
from src.models.recipe import Recipe


@timeit
def get_ordered_recipes(recipes: list[Recipe]):
    recipes.sort(key=lambda recipe: recipe.result_item.level, reverse=True)
    ordered_recipes: list[Recipe] = []
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            if ingredient.item_id not in (
                elem.result_item_id for elem in ordered_recipes
            ):
                ordered_recipes.append(ingredient.recipe)

    return ordered_recipes


@timeit
def get_merged_ordered_with_recipe_items(
    session: Session, server_id: int, recipe_ids: list[int], item_ids: list[int]
) -> list[Item]:
    return (
        session.query(Item)
        .join(Ingredient, Ingredient.item_id == Item.id)
        .join(Recipe, Ingredient.recipe_id == Recipe.id)
        .join(Price, Price.item_id == Item.id)
        .filter(
            Recipe.id.not_in(recipe_ids),
            Item.id.in_(item_ids),
            Price.server_id == server_id,
        )
        .order_by(Price.average.desc())
        .all()
    )


@timeit
def get_recipes_to_upgrade_jobs(session: Session, character: Character) -> set[Recipe]:
    recipes: set[Recipe] = set()
    bank_item_ids: list[int] = [item.id for item in character.bank_items]
    for job_info in character.harvest_jobs_infos:
        if job_info.lvl == 200:
            continue

        recipes_job = (
            session.query(Recipe)
            .join(Item, Item.id == Recipe.result_item_id)
            .join(Ingredient, Recipe.id == Ingredient.recipe_id)
            .filter(
                Recipe.job_id == job_info.job_id,
                Item.level.between(job_info.lvl - 40, job_info.lvl),
            )
            .options(joinedload(Recipe.ingredients).subqueryload(Ingredient.item))
            .group_by(Recipe.id, Ingredient.item_id)
            .having(Ingredient.item_id.in_(bank_item_ids))
            .all()
        )
        recipes.update(recipes_job)

    return recipes


@timeit
def get_best_recipe_for_benefits(
    session: Session,
    server_id: int,
    category: CategoryEnum | None = None,
    type_item_id: int | None = None,
    limit=100,
) -> list[Row[tuple[str, float]]]:
    RecipeItemAlias = aliased(Item)
    PriceRecipeItemAlias = aliased(Price)

    IngredientItemAlias = aliased(Item)
    PriceIngredientItemAlias = aliased(Price)

    filters = []
    if category is not None:
        filters.append(TypeItem.category == category)
        if type_item_id is not None:
            filters.append(TypeItem.id == type_item_id)

    return (
        session.query(
            RecipeItemAlias.name,
            (PriceRecipeItemAlias.average - func.sum(PriceIngredientItemAlias.average)),
        )
        .select_from(Recipe)
        .join(Ingredient, Ingredient.recipe_id == Recipe.id)
        .join(IngredientItemAlias, IngredientItemAlias.id == Ingredient.item_id)
        .join(
            PriceIngredientItemAlias,
            PriceIngredientItemAlias.item_id == IngredientItemAlias.id,
        )
        .join(RecipeItemAlias, Recipe.result_item_id == RecipeItemAlias.id)
        .join(
            PriceRecipeItemAlias,
            PriceRecipeItemAlias.item_id == RecipeItemAlias.id,
        )
        .join(TypeItem, RecipeItemAlias.type_item_id == TypeItem.id)
        .filter(PriceIngredientItemAlias.server_id == server_id)
        .filter(
            PriceIngredientItemAlias.server_id == server_id,
            PriceRecipeItemAlias.server_id == server_id,
            *filters,
        )
        .group_by(Recipe.id, RecipeItemAlias.name, PriceRecipeItemAlias.average)
        .order_by(
            (
                PriceRecipeItemAlias.average
                - func.sum(PriceIngredientItemAlias.average)
            ).desc()
        )
        .limit(limit)
        .all()
    )
