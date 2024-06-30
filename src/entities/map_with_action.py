from typing import Any

from pydantic import BaseModel, ConfigDict

from EzreD2Shared.shared.enums import FromDirection
from EzreD2Shared.shared.schemas.zaapi import ZaapiSchema
from src.models.map import Map
from src.models.map_direction import MapDirection
from src.models.waypoint import Waypoint

type ActionMapChange = MapDirection | ZaapiSchema | Waypoint


class MapWithAction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    map: Map
    map_id: int
    current_direction: FromDirection
    from_action: ActionMapChange | None = None

    def __eq__(self, value: Any) -> bool:
        return (
            isinstance(value, MapWithAction)
            and self.map_id == value.map_id
            and self.current_direction == value.current_direction
        )

    def __str__(self) -> str:
        return f"{self.from_action} : {self.from_action}"

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return (self.map_id, self.current_direction).__hash__()
