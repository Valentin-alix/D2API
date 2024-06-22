from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from EzreD2Shared.shared.schemas.token import Token
from src.database import session_local
from src.models.user import User
from src.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


router = APIRouter()


@router.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(session_local),
):
    user = session.query(User).filter(User.email == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not form_data.password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
