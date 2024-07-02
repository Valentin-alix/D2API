from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.schemas.region import RegionSchema
from D2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema
from src.database import session_local
from src.queries.template_found import (
    get_or_create_template_found_place,
    get_template_place_from_config,
    increment_parsed_count_template_map,
)
from src.security.auth import login

router = APIRouter(prefix="/template", dependencies=[Depends(login)])


@router.get(
    "/places/from_config/", response_model=list[TemplateFoundPlacementSchema] | None
)
def get_places_from_config(
    config: ObjectSearchConfig,
    map_id: int | None = None,
    session: Session = Depends(session_local),
):
    places = get_template_place_from_config(session, config, map_id)
    return places


@router.get("/places/or_create", response_model=TemplateFoundPlacementSchema)
def get_places_or_create(
    config: ObjectSearchConfig,
    filename: str,
    region_schema: RegionSchema,
    map_id: int | None = None,
    session: Session = Depends(session_local),
):
    template_found_place = get_or_create_template_found_place(
        session, config, filename, region_schema, map_id
    )
    return template_found_place


@router.put("/template_found_map/{template_found_map_id}/increment_parsed_count")
def increment_count_template_map(
    template_found_map_id: int,
    session: Session = Depends(session_local),
):
    increment_parsed_count_template_map(session, template_found_map_id)
