from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.enums import CategoryEnum
from EzreD2Shared.shared.schemas.type_item import TypeItemSchema
from src.database import session_local
from src.models.items.type_item import TypeItem

router = APIRouter(prefix="/type_item")


@router.get("/", response_model=list[TypeItemSchema])
def get_type_items(
    category: CategoryEnum | None = None,
    session: Session = Depends(session_local),
):
    if category is not None:
        extra_filters = (TypeItem.category == category,)
    else:
        extra_filters = ()
    type_items = session.query(TypeItem).filter(*extra_filters).all()
    return type_items
