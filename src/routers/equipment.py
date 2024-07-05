from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from src.database import session_local
from src.models.rune import Equipment, Line
from src.queries.utils import get_or_create

router = APIRouter(prefix="/equipment")


@router.post("/", response_model=ReadEquipmentSchema)
def create_equipment(
    equipment_datas: UpdateEquipmentSchema, session: Session = Depends(session_local)
):
    equipment = Equipment(label=equipment_datas.label)
    session.add(equipment)
    session.flush()

    line_instances: list[Line] = []
    for line_schema in equipment_datas.lines:
        line = get_or_create(
            session, Line, False, **line_schema.model_dump(), equipment_id=equipment.id
        )[0]
        line_instances.append(line)

    session.commit()
    return equipment


@router.put("/{equipment_id}", response_model=ReadEquipmentSchema)
def update_equipment(
    equipment_id: int,
    equipment_datas: UpdateEquipmentSchema,
    session: Session = Depends(session_local),
):
    equipment = session.get_one(Equipment, equipment_id)

    line_instances: list[Line] = []
    for line_schema in equipment_datas.lines:
        line = get_or_create(
            session, Line, False, **line_schema.model_dump(), equipment_id=equipment_id
        )[0]
        line_instances.append(line)

    equipment.label = equipment_datas.label
    session.commit()
    return equipment


@router.delete("/{equipment_id}")
def delete_equipment(equipment_id: int, session: Session = Depends(session_local)):
    equipment = session.get(Equipment, equipment_id)
    session.delete(equipment)
    session.commit()


@router.get("/", response_model=list[ReadEquipmentSchema])
def get_equipments(session: Session = Depends(session_local)):
    equipments = session.query(Equipment).all()
    return equipments
