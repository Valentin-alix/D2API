from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.recipe import RecipeSchema
from src.database import session_local
from src.models.config.character import Character
from src.queries.recipe import (
    get_best_recipe_for_benefits,
    get_ordered_recipes,
    get_recipes_to_upgrade_jobs,
)

router = APIRouter(prefix="/recipe")


@router.get("/craft_default", response_model=list[RecipeSchema])
def get_default_recipes(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    craft_items = list(get_recipes_to_upgrade_jobs(session, character))
    ordered_recipes = get_ordered_recipes(craft_items)
    return ordered_recipes


@router.get("/best_recipe_benefits/", response_model=list[tuple[str, float]])
def best_recipe_benefits(
    server_id: int,
    category: CategoryEnum | None = None,
    type_item_id: int | None = None,
    limit: int = 100,
    session: Session = Depends(session_local),
):
    return get_best_recipe_for_benefits(
        session, server_id, category, type_item_id, limit
    )
