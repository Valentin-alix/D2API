import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from D2Shared.shared.schemas.user import CreateUserSchema, ReadUserSchema
from src.models.user import User
from dateutil.relativedelta import relativedelta
from src.security.auth import login, login_for_admin

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ReadUserSchema)
def get_user_me(user: Annotated[HTTPBasicCredentials, Depends(login)]):
    return user


@router.post("/", response_model=ReadUserSchema)
def create_user(
    user_datas: CreateUserSchema, session: Session = Depends(login_for_admin)
):
    user = User(
        **user_datas.model_dump(),
        sub_expire=datetime.datetime.now() + relativedelta(years=1),
    )
    session.add(user)
    session.commit()
    return user
