from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models.users import User
from models.raffle import Raffle
from models.raffleset import RaffleSet
from models.buyer import Buyer
from models.project import Project
from schemas.raffle import RaffleUpdate, RaffleResponse, RaffleSell, RaffleFilters
from routes import get_record_by_composite_key, update_record
from typing import List

router = APIRouter()

@router.get("/project/{project_number}/raffle/{raffle_number}", response_model=RaffleResponse)
def get_raffle(
    project_number: int = Path(..., ge=1),
    raffle_number: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener una rifa específica por su número dentro de un proyecto."""
    return get_record_by_composite_key(db, Raffle, current_user.id,
                                      project_number=project_number, raffle_number=raffle_number)

@router.post("/project/{project_number}/raffles", response_model=List[RaffleResponse])
def get_raffles_filtered(
    project_number: int,
    filters: RaffleFilters,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener rifas con filtros específicos para facilitar sorteos.
    Las rifas están organizadas por proyecto.
    """

    # Verificar que el proyecto pertenece al usuario
    get_record_by_composite_key(db, Project, current_user.id, project_number=project_number)

    # Construir query base
    query = db.query(Raffle).filter(
        Raffle.user_id == current_user.id,
        Raffle.project_number == project_number
    )

    # Aplicar filtros opcionales
    if filters.payment_method:
        query = query.filter(Raffle.payment_method == filters.payment_method)
    if filters.state:
        query = query.filter(Raffle.state == filters.state)
    if filters.set_number:
        query = query.filter(Raffle.set_number == filters.set_number)

    # Ordenar por número de rifa
    query = query.order_by(Raffle.raffle_number)

    # Aplicar límites
    if filters.offset > 0:
        query = query.offset(filters.offset)
    if filters.limit > 0:
        query = query.limit(filters.limit)

    return query.all()

@router.put("/project/{project_number}/raffle", response_model=RaffleResponse)
def update_raffle(
    project_number: int,
    raffle_update: RaffleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar una rifa existente."""
    return update_record(db, Raffle, raffle_update, current_user)

@router.post("/project/{project_number}/raffle/{raffle_number}/sell", response_model=RaffleResponse)
def sell_raffle(
    project_number: int,
    raffle_number: int,
    sale_data: RaffleSell,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Vender una rifa asignándola a un comprador."""
    # Verificar que la rifa pertenece al usuario
    raffle = get_record_by_composite_key(db, Raffle, current_user.id,
                                        project_number=project_number, raffle_number=raffle_number)

    # Verificar que el comprador pertenece al usuario
    get_record_by_composite_key(db, Buyer, current_user.id, buyer_number=sale_data.buyer_number)

    if raffle.state not in ["available", "reserved"]:
        raise HTTPException(status_code=400, detail="Raffle is not available for payment")

    # Actualizar la rifa con los datos de venta
    raffle.buyer_user_id = current_user.id
    raffle.buyer_number = sale_data.buyer_number
    raffle.payment_method = sale_data.payment_method
    raffle.state = "sold"

    db.commit()
    db.refresh(raffle)
    return raffle
