from sqlalchemy import Row, and_, func
from sqlalchemy.orm import Session, aliased, joinedload

from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.utils.debugger import timeit
from src.models.config.character import Character, CharacterJobInfo
from src.models.ingredient import Ingredient
from src.models.items.item import Item
from src.models.items.type_item import TypeItem
from src.models.price import Price
from src.models.recipe import Recipe


def get_valid_ordered_recipes(
    bank_item_ids: list[int], recipes: list[Recipe], valid_job_ids: list[int]
) -> list[Recipe]:
    recipes.sort(key=lambda recipe: recipe.result_item.level, reverse=True)
    ordered_recipes: list[Recipe] = []
    for recipe in recipes:
        if recipe.job_id not in valid_job_ids:
            continue
        for ingredient in sorted(
            recipe.ingredients, key=lambda elem: elem.item.level, reverse=True
        ):
            if ingredient.item.id not in bank_item_ids:
                break
            if ingredient.item.recipe is None:
                continue
            # get deep recipes for ingredient
            ingredient_recipes = get_valid_ordered_recipes(
                bank_item_ids, [ingredient.item.recipe], valid_job_ids
            )
            ordered_recipes.extend(ingredient_recipes)
        else:
            ordered_recipes.append(recipe)

    return ordered_recipes


@timeit
def get_merged_ordered_with_recipe_items(
    session: Session, server_id: int, recipe_ids: list[int], item_ids: list[int]
) -> list[Item]:
    total_ingredients_subquery = (
        session.query(
            Item.id,
            func.count(Ingredient.id).label("total_ingredient_count"),
        )
        .join(Ingredient, Ingredient.item_id == Item.id)
        .group_by(Item.id)
        .subquery()
    )
    filtered_ingredients_subquery = (
        session.query(
            Item.id,
            func.count(Ingredient.id).label("filtered_ingredient_count"),
        )
        .join(
            Ingredient,
            and_(
                Ingredient.item_id == Item.id, Ingredient.recipe_id.not_in(recipe_ids)
            ),
        )
        .group_by(Item.id)
        .subquery()
    )

    return (
        session.query(Item)
        .join(Ingredient, Ingredient.item_id == Item.id)
        .join(Price, Price.item_id == Item.id)
        .join(total_ingredients_subquery, total_ingredients_subquery.c.id == Item.id)
        .join(
            filtered_ingredients_subquery, filtered_ingredients_subquery.c.id == Item.id
        )
        .filter(
            Item.id.in_(item_ids),
            Price.server_id == server_id,
            total_ingredients_subquery.c.total_ingredient_count
            == filtered_ingredients_subquery.c.filtered_ingredient_count,
        )
        .order_by(Price.average.desc())
        .all()
    )


def get_recipes_for_upgrading_job(
    job_info: CharacterJobInfo, session: Session
) -> list[Recipe]:
    recipes_job = (
        session.query(Recipe)
        .join(Item, Item.id == Recipe.result_item_id)
        .join(Ingredient, Recipe.id == Ingredient.recipe_id)
        .filter(
            Recipe.job_id == job_info.job_id,
            Item.level.between(job_info.lvl - 80, job_info.lvl),
        )
        .group_by(Recipe.id)
        .options(joinedload(Recipe.ingredients).subqueryload(Ingredient.item))
        .all()
    )
    return recipes_job


def get_recipes_for_benefits(job_id: int, session: Session) -> list[Recipe]:
    recipes_job = (
        session.query(Recipe)
        .join(Item, Recipe.result_item_id == Item.id)
        .join(Price, Price.item_id == Item.id)
        .filter(Recipe.job_id == job_id)
        .order_by(Price.average.desc())
        .options(joinedload(Recipe.ingredients).subqueryload(Ingredient.item))
        .all()
    )
    return recipes_job


def get_best_recipes(session: Session, character: Character) -> set[Recipe]:
    recipes: set[Recipe] = set()

    for job_info in character.harvest_jobs_infos:
        if job_info.lvl == 200:
            recipes.update(get_recipes_for_benefits(job_info.job_id, session))
        else:
            recipes.update(get_recipes_for_upgrading_job(job_info, session))

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
