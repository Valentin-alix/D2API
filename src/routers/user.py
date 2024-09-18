import datetime
from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.user import CreateUserSchema, ReadUserSchema
from src.database import session_local
from src.models.user import User
from src.queries.user import populate_config_user
from src.security.auth import login

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ReadUserSchema)
def get_user_me(user: Annotated[HTTPBasicCredentials, Depends(login)]):
    return user


@router.post("/", response_model=ReadUserSchema)
def create_user(
    user_datas: CreateUserSchema, session: Session = Depends(session_local)
):
    related_user = session.query(User).filter(User.email == user_datas.email).first()
    if related_user is None:
        related_user = User(
            **user_datas.model_dump(),
            sub_expire=datetime.datetime.now() + relativedelta(years=1),
        )
        session.add(related_user)
        session.commit()
        populate_config_user(session, related_user.id)
    return related_user
