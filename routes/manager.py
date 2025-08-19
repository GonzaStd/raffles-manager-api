from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.entity import Entity
from models.manager import Manager
from schemas.manager import ManagerUpdate, ManagerResponse
from routes import (get_records_filtered, update_record_by_composite_key, delete_record,
                   get_record_by_composite_key)
from typing import List
from auth.services.entity_auth_service import get_current_entity

router = APIRouter()

@router.get("/manager/{manager_number}", response_model=ManagerResponse)
def get_manager(
    manager_number: int,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Get a specific manager by their number."""
    return get_record_by_composite_key(db, Manager, current_entity.id, manager_number=manager_number)

@router.get("/managers", response_model=List[ManagerResponse])
def get_managers(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Get all managers for the current entity."""
    return get_records_filtered(db, Manager, current_entity.id, None, limit, offset)

@router.put("/manager", response_model=ManagerResponse)
def update_manager(
    manager_update: ManagerUpdate,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Update an existing manager."""
    pk_fields = {'manager_number': manager_update.manager_number}
    updates = {k: v for k, v in manager_update.model_dump(exclude_unset=True).items() if k != 'manager_number'}
    return update_record_by_composite_key(db, Manager, current_entity.id, updates, **pk_fields)

@router.delete("/manager/{manager_number}")
def delete_manager(
    manager_number: int,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Delete a manager by number."""
    manager = get_record_by_composite_key(db, Manager, current_entity.id, manager_number=manager_number)
    return delete_record(db, manager, current_entity.id)
