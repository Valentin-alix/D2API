from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from src.security.auth import login

router = APIRouter(prefix="/login")


@router.get("/", response_model=None)
def is_login(user: Annotated[HTTPBasicCredentials, Depends(login)]): ...
