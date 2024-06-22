from datetime import datetime
from typing import Annotated

import jwt
from sqlalchemy.orm import Session
from EzreD2Shared.shared.schemas.token import TokenData
from src.database import session_local
from src.models.user import User
from src.security.auth import oauth2_scheme
from fastapi import Depends, HTTPException, status

from src.security.auth import SECRET_KEY
from src.security.auth import ALGORITHM


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(session_local),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = session.query(User).filter(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_sub_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.sub_expire < datetime.now():
        raise HTTPException(status_code=400, detail="User is not sub anymore")
    return current_user
