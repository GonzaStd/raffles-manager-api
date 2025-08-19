from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.entity import Entity
from models.buyer import Buyer
from schemas.buyer import BuyerCreate, BuyerUpdate, BuyerResponse, BuyerDeleteByNamePhone
from routes import (get_records_filtered, create_record, update_record_by_composite_key, delete_record,
                   get_buyer_by_name_phone, get_record_by_composite_key, get_next_buyer_number)
from typing import List
from auth.services.entity_auth_service import get_current_active_manager, get_current_entity_or_manager

router = APIRouter()

@router.post("/buyer", response_model=BuyerResponse)
def create_buyer(
    buyer: BuyerCreate,
    db: Session = Depends(get_db),
    current_manager = Depends(get_current_active_manager)
):
    """Create a new buyer with auto-increment per entity. Only managers can create buyers."""
    entity_id = current_manager.entity_id
    created_by_manager_number = current_manager.manager_number
    buyer_number = get_next_buyer_number(db, entity_id)
    new_buyer = Buyer(
        entity_id=entity_id,
        buyer_number=buyer_number,
        name=buyer.name,
        phone=buyer.phone,
        email=str(buyer.email) if buyer.email else None,
        created_by_manager_number=created_by_manager_number
    )
    return create_record(db, new_buyer)

@router.get("/buyer/{buyer_number}", response_model=BuyerResponse)
def get_buyer(
    buyer_number: int,
    db: Session = Depends(get_db),
    current_manager = Depends(get_current_active_manager)
):
    """Get a specific buyer by their number."""
    entity_id = current_manager.entity_id
    return get_record_by_composite_key(db, Buyer, entity_id, buyer_number=buyer_number)

@router.get("/buyers", response_model=List[BuyerResponse])
def get_buyers(
    limit: int = 0,
    offset: int = 0,
    created_by_manager_number: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Get buyers for the current entity or manager. Manager: only their buyers. Entity: all buyers, can filter by manager."""
    # Determine user type
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    if user_type == "manager":
        entity_id = user.entity_id
        filters = {"created_by_manager_number": user.manager_number} # Ignores query parameter
    else:
        entity_id = user.id
        filters = {}
        if created_by_manager_number is not None:
            filters["created_by_manager_number"] = created_by_manager_number
    return get_records_filtered(db, Buyer, entity_id, filters, limit, offset)

@router.put("/buyer", response_model=BuyerResponse)
def update_buyer(
    buyer_update: BuyerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Update an existing buyer. Managers can only update buyers they created. Entities can update any buyer."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    buyer = get_record_by_composite_key(db, Buyer, entity_id, buyer_number=buyer_update.buyer_number)
    if user_type == "manager" and buyer.created_by_manager_number != user.manager_number:
        raise HTTPException(status_code=403, detail="Managers can only update buyers they created.")
    pk_fields = {'buyer_number': buyer_update.buyer_number}
    updates = {k: v for k, v in buyer_update.model_dump(exclude_unset=True).items() if k != 'buyer_number'}
    return update_record_by_composite_key(db, Buyer, entity_id, updates, **pk_fields)

@router.delete("/buyer/{buyer_number}")
def delete_buyer_by_number(
    buyer_number: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Delete a buyer by number. Managers can only delete buyers they created. Entities can delete any buyer."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    buyer = get_record_by_composite_key(db, Buyer, entity_id, buyer_number=buyer_number)
    if user_type == "manager" and buyer.created_by_manager_number != user.manager_number:
        raise HTTPException(status_code=403, detail="Managers can only delete buyers they created.")
    return delete_record(db, buyer, entity_id)

@router.delete("/buyer/by-name-phone")
def delete_buyer_by_name_phone(
    buyer_data: BuyerDeleteByNamePhone,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Delete a buyer by unique name-phone combination. Managers can only delete buyers they created. Entities can delete any buyer."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    buyer = get_buyer_by_name_phone(db, buyer_data.name, buyer_data.phone, entity_id)
    if user_type == "manager" and buyer.created_by_manager_number != user.manager_number:
        raise HTTPException(status_code=403, detail="Managers can only delete buyers they created.")
    return delete_record(db, buyer, entity_id)
