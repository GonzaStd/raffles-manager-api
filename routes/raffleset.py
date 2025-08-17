from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models.users import User
from models.raffleset import RaffleSet
from models.project import Project
from models.raffle import Raffle
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate, RaffleSetResponse
from routes import get_record, get_records, create_record, update_record, delete_record
from typing import List

router = APIRouter()


@router.post("/raffleset", response_model=RaffleSetResponse)
def create_raffleset(
    raffleset: RaffleSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo set de rifas con numeración automática y creación de rifas individuales."""
    # Verificar que el proyecto pertenece al usuario usando función optimizada
    get_record(db, Project, raffleset.project_id, current_user)

    # Encontrar el último número de rifa para este PROYECTO específico del usuario
    # Los números de rifas son continuos a través de todos los sets dentro de un proyecto
    last_number = (
        db.query(Raffle.number)
        .join(RaffleSet, Raffle.set_id == RaffleSet.id)
        .filter(
            RaffleSet.project_id == raffleset.project_id,
            Raffle.user_id == current_user.id
        )
        .order_by(Raffle.number.desc())
        .limit(1)
        .scalar()
    )

    # Calcular automáticamente init y final basándose en la última rifa del proyecto
    if last_number is None:
        # Si no hay rifas previas en este proyecto, empezar desde 1
        init_number = 1
    else:
        # Continuar desde el siguiente número después de la última rifa
        init_number = last_number + 1

    final_number = init_number + raffleset.quantity - 1

    # Crear nuevo RaffleSet con los números calculados automáticamente
    new_raffleset = RaffleSet(
        name=raffleset.name,
        project_id=raffleset.project_id,
        user_id=current_user.id,
        type=raffleset.type,
        init=init_number,
        final=final_number,
        unit_price=raffleset.unit_price
    )

    # Crear el set primero
    created_set = create_record(db, new_raffleset)

    # Crear automáticamente todas las rifas individuales del rango
    raffles_to_create = []
    for number in range(init_number, final_number + 1):
        new_raffle = Raffle(
            number=number,
            set_id=created_set.id,
            user_id=current_user.id,
            state="available"
        )
        raffles_to_create.append(new_raffle)

    # Insertar todas las rifas en batch para eficiencia
    try:
        db.add_all(raffles_to_create)
        db.commit()
    except Exception as e:
        db.rollback()
        # Si fallan las rifas, eliminar el set creado para mantener consistencia
        db.delete(created_set)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating raffles: {str(e)}"
        )

    return created_set


@router.get("/raffleset/{raffleset_id}", response_model=RaffleSetResponse)
def get_raffleset(
    raffleset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un set de rifas específico."""
    return get_record(db, RaffleSet, raffleset_id, current_user)


@router.get("/rafflesets", response_model=List[RaffleSetResponse])
def get_rafflesets(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los sets de rifas del usuario."""
    return get_records(db, RaffleSet, current_user, limit, offset)


@router.put("/raffleset", response_model=RaffleSetResponse)
def update_raffleset(
    raffleset_update: RaffleSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un set de rifas existente."""
    return update_record(db, RaffleSet, raffleset_update, current_user)


@router.delete("/raffleset/{raffleset_id}")
def delete_raffleset(
    raffleset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un set de rifas y todas sus rifas asociadas."""
    raffleset = get_record(db, RaffleSet, raffleset_id, current_user)
    return delete_record(db, raffleset, current_user)
