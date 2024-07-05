from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from src.database import session_local
from src.models.user import User


security = HTTPBasic()


def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: Session = Depends(session_local),
) -> User:
    user = session.query(User).filter(User.email == credentials.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username")
    if not credentials.password == user.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    if user.sub_expire < datetime.now():
        raise HTTPException(status_code=401, detail="User is not sub anymore")

    return user


def login_for_admin(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: Session = Depends(session_local),
):
    user = login(credentials, session)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="User is not admin.")
