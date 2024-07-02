from operator import or_
from typing import cast

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from D2Shared.shared.entities.object_search_config import ObjectSearchConfig
from D2Shared.shared.schemas.region import RegionSchema
from D2Shared.shared.schemas.template_found import TemplateFoundPlacementSchema
from src.models.region import Region
from src.models.template_found import (
    TemplateFound,
    TemplateFoundMap,
    TemplateFoundPlacement,
)
from src.queries.utils import get_or_create


def increment_parsed_count_template_map(session: Session, template_found_map_id: int):
    session.query(TemplateFoundMap).filter_by(id=template_found_map_id).update(
        {"parsed_count": TemplateFoundMap.parsed_count + 1}
    )


def get_template_place_from_config(
    session: Session,
    config: ObjectSearchConfig,
    map_id: int | None = None,
) -> list[TemplateFoundPlacementSchema] | None:
    """get template found placement from objet search config (base on config.id)
        if cache is not ready return None
    Args:
        session (Session)
        config (ObjectSearchConfig)
        map_id (int | None, optional): _description_. Defaults to None. provide map_id if objetSearch is not from hud

    Returns:
        list[TemplateFoundPlacement] | None: template found placement linked
    """
    if config.cache_info is None:
        return None

    query = (
        session.query(TemplateFoundMap)
        .join(
            TemplateFoundPlacement,
            TemplateFoundMap.id == TemplateFoundPlacement.template_found_map_id,
        )
        .join(TemplateFound, TemplateFound.id == TemplateFoundMap.template_found_id)
        .filter(TemplateFound.name == config.id)
        .group_by(TemplateFoundMap.id, TemplateFoundPlacement.id)
    )

    if config.cache_info.max_placement is not None:
        count_filter = (
            func.count(TemplateFoundPlacement.id) >= config.cache_info.max_placement
        )
    else:
        count_filter = None

    if config.cache_info.min_parsed_count_on_map is not None:
        query = query.filter(TemplateFoundMap.map_id == map_id)
        if count_filter is not None:
            query = query.having(
                or_(
                    count_filter,
                    TemplateFoundMap.parsed_count
                    >= config.cache_info.min_parsed_count_on_map,
                )
            )
        else:
            query = query.having(
                TemplateFoundMap.parsed_count
                >= config.cache_info.min_parsed_count_on_map
            )
    else:
        if count_filter is not None:
            query = query.having(count_filter)

    template_found_map = query.options(
        joinedload(TemplateFoundMap.templates_found_placement).subqueryload(
            TemplateFoundPlacement.region
        )
    ).one_or_none()

    if template_found_map is not None:
        return cast(
            list[TemplateFoundPlacementSchema],
            template_found_map.templates_found_placement,
        )

    return None


def get_or_create_template_found_place(
    session: Session,
    config: ObjectSearchConfig,
    filename: str,
    region_schema: RegionSchema,
    map_id: int | None = None,
) -> TemplateFoundPlacementSchema:
    assert config.cache_info is not None
    template_found_id = get_or_create(
        session, TemplateFound, name=config.id, commit=True
    )[0].id
    filters_template_map = {"template_found_id": template_found_id}
    if config.cache_info.min_parsed_count_on_map is not None:
        assert map_id is not None
        filters_template_map["map_id"] = map_id
    template_found_map = get_or_create(
        session=session,
        model=TemplateFoundMap,
        options=None,
        defaults=None,
        commit=False,
        **filters_template_map,
    )[0]
    session.flush()
    if (
        template_found_place := session.query(TemplateFoundPlacement)
        .join(Region, Region.id == TemplateFoundPlacement.region_id)
        .filter(
            TemplateFoundPlacement.template_found_map_id == template_found_map.id,
            Region.is_enclosing(region_schema),
        )
        .first()
    ) is None:
        OFFSET_BIGGER_REGION = 5
        bigger_region_shema = RegionSchema(
            top=region_schema.top - OFFSET_BIGGER_REGION,
            left=region_schema.left - OFFSET_BIGGER_REGION,
            right=region_schema.right + OFFSET_BIGGER_REGION,
            bot=region_schema.bot + OFFSET_BIGGER_REGION,
        )
        bigger_related_region = get_or_create(
            session, Region, **bigger_region_shema.model_dump(), commit=False
        )[0]
        template_found_place = TemplateFoundPlacement(
            filename=filename,
            region=bigger_related_region,
            template_found_map_id=template_found_map.id,
        )
        session.add(template_found_place)

    session.flush()
    return cast(TemplateFoundPlacementSchema, template_found_place)
