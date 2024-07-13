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

    for line_schema in equipment_datas.lines:
        session.add(
            Line(
                stat_id=line_schema.stat_id,
                value=line_schema.value,
                equipment_id=equipment.id,
            )
        )

    if equipment_datas.exo_line is not None:
        equipment.exo_line = get_or_create(
            session,
            Line,
            False,
            stat_id=equipment_datas.exo_line.stat_id,
            equipment_id=equipment.id,
        )[0]
        equipment.exo_line.value = equipment_datas.exo_line.value

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
        line = get_or_create(
            session, Line, False, stat_id=line_schema.stat_id, equipment_id=equipment.id
        )[0]
        line.spent_quantity = 0
        line.value = line_schema.value
        line_instances.append(line)

    equipment.count_attempt = 0
    equipment.lines = line_instances
    equipment.label = equipment_datas.label

    if equipment_datas.exo_line is not None:
        equipment.exo_line = get_or_create(
            session,
            Line,
            False,
            stat_id=equipment_datas.exo_line.stat_id,
            equipment_id=equipment.id,
        )[0]
        equipment.exo_line.value = equipment_datas.exo_line.value

    if equipment.exo_line:
        equipment.exo_line.spent_quantity = 0

    session.commit()
    return equipment


@router.put("/{equipment_id}/attempt/", response_model=ReadEquipmentSchema)
def increment_equipment_attempt(
    equipment_id: int,
    session: Session = Depends(session_local),
    user: User = Depends(login),
):
    equipment = session.get_one(Equipment, equipment_id)
    if equipment.user_id != user.id:
        raise HTTPException(403, "Can't update equipment of other users")

    equipment.count_attempt += 1
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
