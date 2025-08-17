from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models.users import User
from models.raffleset import RaffleSet
from models.project import Project
from models.raffle import Raffle
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate, RaffleSetResponse
from routes import (get_records, create_record, update_record, delete_record,
                   get_record_by_composite_key, get_next_set_number, get_next_raffle_number)
from typing import List

router = APIRouter()

@router.post("/project/{project_number}/raffleset", response_model=RaffleSetResponse)
def create_raffleset(
    project_number: int,
    raffleset: RaffleSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo set de rifas con numeración automática y creación de rifas individuales."""
    # Verificar que el proyecto existe y pertenece al usuario
    get_record_by_composite_key(db, Project, current_user.id, project_number=project_number)

    # Obtener el siguiente número de set para este proyecto
    set_number = get_next_set_number(db, current_user.id, project_number)

    # Encontrar el último número de rifa para este proyecto específico del usuario
    last_raffle_number = get_next_raffle_number(db, current_user.id, project_number) - 1

    # Calcular automáticamente init y final basándose en la última rifa del proyecto
    init_number = last_raffle_number + 1 if last_raffle_number > 0 else 1
    final_number = init_number + raffleset.quantity - 1

    # Crear nuevo RaffleSet
    new_raffleset = RaffleSet(
        user_id=current_user.id,
        project_number=project_number,
        set_number=set_number,
        name=raffleset.name,
        type=raffleset.type,
        init=init_number,
        final=final_number,
        unit_price=raffleset.unit_price
    )

    # Crear el set primero
    created_set = create_record(db, new_raffleset)

    # Crear automáticamente todas las rifas individuales del rango
    raffles_to_create = []
    for raffle_num in range(init_number, final_number + 1):
        new_raffle = Raffle(
            user_id=current_user.id,
            project_number=project_number,
            raffle_number=raffle_num,
            set_number=set_number,
            state="available"
        )
        raffles_to_create.append(new_raffle)

    # Insertar todas las rifas en batch
    try:
        db.add_all(raffles_to_create)
        db.commit()
    except Exception as e:
        db.rollback()
        db.delete(created_set)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Error creating raffles: {str(e)}")

    return created_set

@router.get("/project/{project_number}/raffleset/{set_number}", response_model=RaffleSetResponse)
def get_raffleset(
    project_number: int,
    set_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un set de rifas específico."""
    return get_record_by_composite_key(db, RaffleSet, current_user.id,
                                      project_number=project_number, set_number=set_number)

@router.get("/project/{project_number}/rafflesets", response_model=List[RaffleSetResponse])
def get_rafflesets(
    project_number: int,
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los sets de rifas de un proyecto."""
    # Verificar que el proyecto existe
    get_record_by_composite_key(db, Project, current_user.id, project_number=project_number)

    # Filtrar sets por proyecto
    query = db.query(RaffleSet).filter(
        RaffleSet.user_id == current_user.id,
        RaffleSet.project_number == project_number
    ).order_by(RaffleSet.set_number)

    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)

    return query.all()

@router.put("/project/{project_number}/raffleset", response_model=RaffleSetResponse)
def update_raffleset(
    project_number: int,
    raffleset_update: RaffleSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un set de rifas existente."""
    return update_record(db, RaffleSet, raffleset_update, current_user)

@router.delete("/project/{project_number}/raffleset/{set_number}")
def delete_raffleset(
    project_number: int,
    set_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un set de rifas y todas sus rifas asociadas."""
    raffleset = get_record_by_composite_key(db, RaffleSet, current_user.id,
                                           project_number=project_number, set_number=set_number)
    return delete_record(db, raffleset, current_user)
