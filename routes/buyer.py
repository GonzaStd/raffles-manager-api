from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models.users import User
from models.buyer import Buyer
from schemas.buyer import BuyerCreate, BuyerUpdate, BuyerResponse, BuyerDeleteByNamePhone
from routes import (get_records, create_record, update_record, delete_record,
                   get_buyer_by_name_phone, get_record_by_composite_key, get_next_buyer_number)
from typing import List

router = APIRouter()

@router.post("/buyer", response_model=BuyerResponse)
def create_buyer(
    buyer: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo comprador con auto-increment per user."""
    buyer_number = get_next_buyer_number(db, current_user.id)

    new_buyer = Buyer(
        user_id=current_user.id,
        buyer_number=buyer_number,
        name=buyer.name,
        phone=buyer.phone,
        email=str(buyer.email) if buyer.email else None
    )
    return create_record(db, new_buyer)

@router.get("/buyer/{buyer_number}", response_model=BuyerResponse)
def get_buyer(
    buyer_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un comprador específico por su número."""
    return get_record_by_composite_key(db, Buyer, current_user.id, buyer_number=buyer_number)

@router.get("/buyers", response_model=List[BuyerResponse])
def get_buyers(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los compradores del usuario."""
    return get_records(db, Buyer, current_user, limit, offset)

@router.put("/buyer", response_model=BuyerResponse)
def update_buyer(
    buyer_update: BuyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un comprador existente."""
    return update_record(db, Buyer, buyer_update, current_user)

@router.delete("/buyer/{buyer_number}")
def delete_buyer_by_number(
    buyer_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un comprador por número."""
    buyer = get_record_by_composite_key(db, Buyer, current_user.id, buyer_number=buyer_number)
    return delete_record(db, buyer, current_user)

@router.delete("/buyer/by-name-phone")
def delete_buyer_by_name_phone(
    buyer_data: BuyerDeleteByNamePhone,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un comprador por nombre-teléfono único."""
    buyer = get_buyer_by_name_phone(db, buyer_data.name, buyer_data.phone, current_user)
    return delete_record(db, buyer, current_user)
