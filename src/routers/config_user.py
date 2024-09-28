import json

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.config_user import (
    ReadConfigUserSchema,
    UpdateConfigUserSchema,
)
from src.database import session_local
from src.models.user import ConfigUser, RangeWait
from src.queries.utils import get_or_create
from src.security.auth import login

router = APIRouter(prefix="/config_user", dependencies=[Depends(login)])


@router.put("/{config_user_id}/", response_model=ReadConfigUserSchema)
async def update_config_user(
    config_user_id: int,
    request: Request,  # workaround to load time fields
    session: Session = Depends(session_local),
):
    content = await request.json()
    config_user_schema = UpdateConfigUserSchema(**json.loads(content))
    config_user_instance: ConfigUser = session.get_one(ConfigUser, config_user_id)

    # wait new map
    range_new_map_instance = get_or_create(
        session,
        RangeWait,
        **config_user_schema.range_new_map.model_dump(),
    )[0]
    config_user_instance.range_new_map = range_new_map_instance

    # normal fields
    config_user_datas = config_user_schema.model_dump(exclude_unset=True)
    for key, value in config_user_datas.items():
        if key in ["ranges_hour_playtime", "range_new_map"]:
            continue
        setattr(config_user_instance, key, value)
    session.commit()
    return config_user_instance
