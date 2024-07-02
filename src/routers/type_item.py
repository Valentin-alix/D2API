from fastapi import APIRouter, Depends
from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

from D2Shared.shared.enums import CategoryEnum
from D2Shared.shared.schemas.type_item import TypeItemSchema
from src.database import session_local
from src.models.type_item import TypeItem
from src.security.auth import login

router = APIRouter(prefix="/type_item", dependencies=[Depends(login)])


@router.get("/", response_model=list[TypeItemSchema])
def get_type_items(
    category: CategoryEnum | None = None,
    session: Session = Depends(session_local),
):
    extra_filters: tuple[ColumnElement[bool]] | tuple = ()
    if category is not None:
        extra_filters = (TypeItem.category == category,)

    type_items = session.query(TypeItem).filter(*extra_filters).all()
    return type_items
