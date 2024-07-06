from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from D2Shared.shared.schemas.equipment import ReadEquipmentSchema, UpdateEquipmentSchema
from src.database import session_local
from src.models.equipment import Equipment
from src.models.rune import Line
from src.models.user import User
from src.queries.utils import get_or_create
from src.security.auth import login

router = APIRouter(prefix="/equipment")


@router.post("/", response_model=ReadEquipmentSchema)
def create_equipment(
    equipment_datas: UpdateEquipmentSchema,
    session: Session = Depends(session_local),
    user: User = Depends(login),
):
    equipment = Equipment(label=equipment_datas.label, user_id=user.id)
    session.add(equipment)
    session.flush()

    line_instances: list[Line] = []
    for line_schema in equipment_datas.lines:
        line_datas: dict = {
            "stat_id": line_schema.stat_id,
            "value": line_schema.value,
            "equipment_id": equipment.id,
        }
        line = get_or_create(
            session=session,
            model=Line,
            commit=False,
            **line_datas,
        )[0]
        line_instances.append(line)

    session.commit()
    return equipment


@router.put("/{equipment_id}", response_model=ReadEquipmentSchema)
def update_equipment(
    equipment_id: int,
    equipment_datas: UpdateEquipmentSchema,
    session: Session = Depends(session_local),
    user: User = Depends(login),
):
    equipment = session.get_one(Equipment, equipment_id)
    if equipment.user_id != user.id:
        raise HTTPException(403, "Can't update equipment of other users")

    line_instances: list[Line] = []
    for line_schema in equipment_datas.lines:
        line_datas: dict = {
            "stat_id": line_schema.stat_id,
            "value": line_schema.value,
            "equipment_id": equipment.id,
        }
        line = get_or_create(session, Line, False, **line_datas)[0]
        line_instances.append(line)

    equipment.label = equipment_datas.label
    session.commit()
    return equipment


@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    session: Session = Depends(session_local),
    user: User = Depends(login),
):
    equipment = session.get_one(Equipment, equipment_id)
    if equipment.user_id != user.id:
        raise HTTPException(403, "Can't delete equipment of other users")
    session.delete(equipment)
    session.commit()


@router.get("/", response_model=list[ReadEquipmentSchema])
def get_equipments(
    session: Session = Depends(session_local),
    user: User = Depends(login),
):
    equipments = session.query(Equipment).filter(Equipment.user_id == user.id).all()
    return equipments
