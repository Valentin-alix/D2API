from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from D2Shared.shared.schemas.config_user import (
    ReadConfigUserSchema,
    UpdateConfigUserSchema,
)
from src.models.user import ConfigUser, RangeHourPlayTime, RangeWait
from src.queries.utils import get_or_create
from src.security.auth import login_for_admin

router = APIRouter(prefix="/config_user")


@router.put("/{config_user_id}/", response_model=ReadConfigUserSchema)
def update_config_user(
    config_user_id: int,
    config_user_schema: UpdateConfigUserSchema,
    session: Session = Depends(login_for_admin),
):
    config_user_instance: ConfigUser = session.get_one(ConfigUser, config_user_id)

    # playtimes
    range_hour_playtime_instances: list[RangeHourPlayTime] = [
        get_or_create(
            session,
            RangeHourPlayTime,
            **elem.model_dump(),
            config_user_id=config_user_id,
        )[0]
        for elem in config_user_schema.ranges_hour_playtime
    ]
    config_user_instance.ranges_hour_playtime = range_hour_playtime_instances

    # wait new map
    range_new_map_instance = get_or_create(
        session, RangeWait, **config_user_schema.range_new_map.model_dump()
    )[0]
    config_user_instance.range_new_map = range_new_map_instance

    # wait
    range_wait_instance = get_or_create(
        session, RangeWait, **config_user_schema.range_wait.model_dump()
    )[0]
    config_user_instance.range_wait = range_wait_instance

    # normal fields
    config_user_datas = config_user_schema.model_dump(exclude_unset=True)
    for key, value in config_user_datas.items():
        if isinstance(value, BaseModel):
            continue
        setattr(config_user_instance, key, value)
    session.commit()
    return config_user_instance
