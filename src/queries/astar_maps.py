from typing import Iterator

from sqlalchemy.orm import Session, joinedload

from EzreD2Shared.shared.directions import get_inverted_direction
from EzreD2Shared.shared.enums import FromDirection
from EzreD2Shared.shared.utils.algos.astar import Astar
from EzreD2Shared.shared.utils.randomizer import multiply_offset
from src.entities.map_with_action import MapWithAction
from src.models.navigations.map import Map
from src.models.navigations.waypoint import Waypoint
from src.queries.map import get_neighbors
from src.queries.zaapi import get_zaapis_by_zone


def is_goal_reached_path_map(
    start_map_with_action: MapWithAction, end_maps_with_action: set[MapWithAction]
):
    return start_map_with_action.map in (elem.map for elem in end_maps_with_action)


def get_dist_map_to_end_maps(
    map_with_action: MapWithAction, end_maps_with_action: set[MapWithAction]
) -> float:
    return (
        min(map_with_action.map.get_dist_map(elem.map) for elem in end_maps_with_action)
        * multiply_offset()
    )


def get_neighbors_map_change(
    map_with_action: "MapWithAction",
    is_sub: bool,
    use_transport: bool,
    available_waypoints_ids: list[int],
    checked_world_id_waypoints: set[int],
    session: Session,
):
    neighbors_maps_with_action: set[MapWithAction] = set(
        (
            MapWithAction(
                map=map_direction.to_map,
                current_direction=get_inverted_direction(map_direction.to_direction),
                from_action=map_direction,
            )
        )
        for map_direction in get_neighbors(
            session, map_with_action.map.id, map_with_action.current_direction
        )
    )

    if is_sub and use_transport:
        if (
            map_with_action.map.world_id not in checked_world_id_waypoints
            and map_with_action.map.allow_teleport_from
        ):
            waypoints = (
                session.query(Waypoint)
                .join(Map, Waypoint.map_id == Map.id)
                .filter(
                    Waypoint.id.in_(available_waypoints_ids),
                    Map.world_id == map_with_action.map.world_id,
                )
                .options(joinedload(Waypoint.map))
            )
            for waypoint in waypoints:
                neighbors_maps_with_action.add(
                    MapWithAction(
                        map=waypoint.map,
                        current_direction=FromDirection.WAYPOINT,
                        from_action=waypoint,
                    )
                )
            checked_world_id_waypoints.add(map_with_action.map.world_id)

        for zappis in get_zaapis_by_zone(session).values():
            if not any(elem.id == map_with_action.map.id for elem in zappis.keys()):
                continue

            for map, zaapi in zappis.items():
                neighbors_maps_with_action.add(
                    MapWithAction(
                        map=map,
                        current_direction=FromDirection.ZAAPI,
                        from_action=zaapi,
                    )
                )

    return iter(neighbors_maps_with_action)


class AstarMap(Astar):
    def __init__(
        self,
        is_sub: bool,
        use_transport: bool,
        available_waypoint_ids: list[int],
        session: Session,
    ) -> None:
        self.is_sub = is_sub
        self.session = session
        self.use_transport = use_transport
        self.available_waypoints_ids = available_waypoint_ids
        self.checked_world_id_waypoints: set[int] = set()
        super().__init__()

    def find_path(
        self,
        start_map: Map,
        current_direction: FromDirection,
        end_maps: list[Map],
    ) -> Iterator[MapWithAction] | None:
        start = MapWithAction(map=start_map, current_direction=current_direction)
        ends = set(
            (
                MapWithAction(map=map, current_direction=current_direction)
                for map in end_maps
            )
        )
        return super().find_path(start, ends)

    def is_goal_reached(self, current: MapWithAction, ends: set[MapWithAction]) -> bool:
        return is_goal_reached_path_map(current, ends)

    def get_dist(self, current: MapWithAction, ends: set[MapWithAction]) -> float:
        return get_dist_map_to_end_maps(current, ends)

    def get_neighbors(self, data: MapWithAction) -> Iterator[MapWithAction]:
        return get_neighbors_map_change(
            data,
            self.is_sub,
            self.use_transport,
            self.available_waypoints_ids,
            self.checked_world_id_waypoints,
            self.session,
        )
