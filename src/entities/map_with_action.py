from typing import Any

from pydantic import BaseModel, ConfigDict

from D2Shared.shared.enums import ToDirection
from D2Shared.shared.schemas.zaapi import ZaapiSchema
from src.models.map import Map
from src.models.waypoint import Waypoint


type ActionMapChange = ToDirection | ZaapiSchema | Waypoint


class MapWithAction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    map: Map
    map_id: int
    from_action: ActionMapChange | None = None

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, MapWithAction) and self.map_id == value.map_id

    def __str__(self) -> str:
        return f"{self.from_action} : {self.from_action}"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.map_id.__hash__()
