import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from EzreD2Shared.shared.schemas.user import CreateUserSchema, ReadUserSchema
from src.database import session_local
from src.models.user import User
from src.queries.auth import get_current_sub_user
from dateutil.relativedelta import relativedelta

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ReadUserSchema)
def get_user_me(current_user: Annotated[ReadUserSchema, Depends(get_current_sub_user)]):
    return current_user


@router.post("/", response_model=ReadUserSchema)
def create_user(
    create_user: CreateUserSchema, session: Session = Depends(session_local)
):
    user = User(
        **create_user.model_dump(),
        sub_expire=datetime.datetime.now() + relativedelta(month=1)
    )
    session.add(user)
    session.commit()
    return user
