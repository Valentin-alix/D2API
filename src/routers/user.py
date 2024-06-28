import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from EzreD2Shared.shared.schemas.user import CreateUserSchema, ReadUserSchema
from src.models.user import User
from dateutil.relativedelta import relativedelta
from src.security.auth import login

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ReadUserSchema)
def get_user_me(user: Annotated[HTTPBasicCredentials, Depends(login)]):
    return user


@router.post("/", response_model=ReadUserSchema)
def create_user(user: CreateUserSchema, session: Session = Depends(login)):
    user = User(
        **user.model_dump(),
        sub_expire=datetime.datetime.now() + relativedelta(years=1)
    )
    session.add(user)
    session.commit()
    return user
