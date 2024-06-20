from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.price import PriceSchema
from src.database import session_local
from src.models.price import Price

router = APIRouter(prefix="/price")


@router.post("/update_or_create/", response_model=PriceSchema)
def update_or_create_price(
    item_id: int,
    server_id: int,
    price_average: float,
    session: Session = Depends(session_local),
):
    price = (
        session.query(Price)
        .filter(Price.server_id == server_id, Price.item_id == item_id)
        .one_or_none()
    )
    if price is None:
        price = Price(item_id=item_id, server_id=server_id)
        session.add(price)
    price.average = price_average
    session.commit()
    return price
