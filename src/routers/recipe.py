from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.consts.jobs import HARVEST_JOBS_NAME
from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.database import session_local
from src.models.character import Character
from src.models.character_job_info import CharacterJobInfo
from src.models.job import Job
from src.models.recipe import Recipe
from src.queries.recipe import (
    get_available_recipes,
    get_best_recipe_for_benefits,
    get_valid_ordered_recipes_query,
)
from src.security.auth import login

router = APIRouter(prefix="/recipe", dependencies=[Depends(login)])


@router.get("/valid_ordered/", response_model=list[RecipeSchema])
def get_valid_ordered_recipes(
    character_id: str,
    recipe_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    bank_items = [elem.id for elem in character.bank_items]
    recipes = session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()

    ordered_valid_recipes = get_valid_ordered_recipes_query(
        bank_items, recipes, character.harvest_jobs_infos
    )
    return ordered_valid_recipes


@router.get("/available/", response_model=list[RecipeSchema])
def available_recipes(
    character_id: str,
    session: Session = Depends(session_local),
):
    harvest_job_infos: list[CharacterJobInfo] = (
        session.query(CharacterJobInfo)
        .join(Job, CharacterJobInfo.job_id == Job.id)
        .filter(
            CharacterJobInfo.character_id == character_id,
            Job.name.in_(HARVEST_JOBS_NAME),
        )
        .all()
    )
    return get_available_recipes(session, harvest_job_infos)


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
