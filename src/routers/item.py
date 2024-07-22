from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.item import ItemSchema
from src.database import session_local
from src.models.character import Character
from src.models.icon import Icon
from src.models.item import Item
from src.queries.recipe import (
    get_merged_ordered_with_recipe_items,
)
from src.security.auth import login

router = APIRouter(prefix="/item", dependencies=[Depends(login)])


@router.get("/{item_id}/image/", response_class=Response)
def get_icon_img(
    item_id: int,
    session: Session = Depends(session_local),
):
    img = (
        session.query(Icon.image)
        .join(Item, Item.icon_id == Icon.id)
        .filter(Item.id == item_id)
        .first()
    )
    if img is None:
        return Response()

    return Response(content=img[0])


@router.get("/default_sellable", response_model=list[ItemSchema])
def get_default_sellable(
    character_id: str,
    recipe_ids: list[int],
    session: Session = Depends(session_local),
):
    character = session.get_one(Character, character_id)
    sell_items = get_merged_ordered_with_recipe_items(
        session,
        character.server_id,
        recipe_ids,
        [_item.id for _item in character.bank_items],
    )
    return sell_items
