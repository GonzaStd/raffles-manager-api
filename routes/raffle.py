from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models import Project
from models.users import User
from models.raffle import Raffle
from models.raffleset import RaffleSet
from models.buyer import Buyer
from schemas.raffle import RaffleUpdate, RaffleResponse, RaffleSell, RaffleFilters
from routes import get_record, update_record, get_records
from typing import List

router = APIRouter()

@router.get("/raffle/{raffle_number}", response_model=RaffleResponse)
def get_raffle(
    raffle_number: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener una rifa específica por su número."""
    return get_record(db, Raffle, raffle_number, current_user)  # Correcto: pasar current_user

@router.post("/raffles", response_model=List[RaffleResponse])
def get_raffles_filtered(
    filters: RaffleFilters,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener rifas con filtros específicos para facilitar sorteos.
    Las rifas están organizadas por proyecto, por lo que project_id es obligatorio.
    """

    # Validar que project_id sea obligatorio
    if not filters.project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required for filtering raffles"
        )

    # Verificar que el proyecto pertenece al usuario
    get_record(db, Project, filters.project_id, current_user)  # Correcto: pasar current_user

    # Preparar filtros directos del modelo Raffle
    raffle_filters = {}
    if filters.payment_method:
        raffle_filters['payment_method'] = filters.payment_method
    if filters.state:
        raffle_filters['state'] = filters.state
    if filters.set_id:
        raffle_filters['set_id'] = filters.set_id

    # Configurar JOIN con raffle_sets
    join_config = [{
        'model': RaffleSet,
        'condition': Raffle.set_id == RaffleSet.id,
        'filter': {'project_id': filters.project_id}
    }]

    # Ejecutar consulta optimizada
    return get_records(
        db=db,
        Model=Raffle,
        current_user=current_user,  # Correcto: pasar current_user
        limit=filters.limit,
        offset=filters.offset,
        filters=raffle_filters,
        joins=join_config
    )

@router.put("/raffle", response_model=RaffleResponse)
def update_raffle(
    raffle_update: RaffleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar una rifa existente."""
    return update_record(db, Raffle, raffle_update, current_user)  # Correcto: pasar current_user

@router.post("/raffle/{raffle_number}/sell", response_model=RaffleResponse)
def sell_raffle(
    raffle_number: int,
    sale_data: RaffleSell,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Vender una rifa asignándola a un comprador."""
    # Verificar que la rifa pertenece al usuario
    raffle = get_record(db, Raffle, raffle_number, current_user)  # Correcto: pasar current_user

    # Verificar que el comprador pertenece al usuario
    get_record(db, Buyer, sale_data.buyer_id, current_user)  # Correcto: pasar current_user

    if raffle.state not in ["available", "reserved"]:
        raise HTTPException(status_code=400, detail="Raffle is not available for payment")

    # Actualizar la rifa con los datos de venta
    raffle.buyer_id = sale_data.buyer_id
    raffle.payment_method = sale_data.payment_method
    raffle.state = "sold"

    db.commit()
    db.refresh(raffle)
    return raffle
