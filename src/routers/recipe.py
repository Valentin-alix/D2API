from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.consts.jobs import HARVEST_JOBS_NAME
from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.recipe import RecipeSchema
from src.database import session_local
from src.models.character import Character
from src.models.job import Job
from src.queries.recipe import (
    get_best_recipe_for_benefits,
    get_best_recipes,
    get_valid_ordered_recipes,
)
from src.security.auth import login

router = APIRouter(prefix="/recipe", dependencies=[Depends(login)])


@router.get("/craft_default", response_model=list[RecipeSchema])
def get_default_recipes(
    character_id: str,
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    bank_item_ids: list[int] = [elem.id for elem in character.bank_items]
    best_recipes = list(get_best_recipes(session, character))

    harvest_job_ids: list[int] = [
        elem[0]
        for elem in session.query(Job.id).filter(Job.name.in_(HARVEST_JOBS_NAME)).all()
    ]
    ordered_valid_recipes = get_valid_ordered_recipes(
        bank_item_ids, best_recipes, harvest_job_ids
    )
    return ordered_valid_recipes


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
