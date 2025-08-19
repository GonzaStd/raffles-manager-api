from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, Optional

from models.entity import Entity


def get_next_number(db: Session, Model, entity_id: int, filters: Optional[Dict[str, Any]] = None) -> int:
    """
    Universal auto-increment function for any model with composite PKs.

    Args:
        db: Database session
        Model: SQLAlchemy model class
        entity_id: Entity ID for filtering
        filters: Additional filters for scoping (e.g., {'project_number': 1})

    Returns:
        Next available number for the specified scope
    """
    # Determine which column is the auto-increment field
    number_field = None
    if hasattr(Model, 'buyer_number'):
        number_field = Model.buyer_number
    elif hasattr(Model, 'project_number'):
        number_field = Model.project_number
    elif hasattr(Model, 'set_number'):
        number_field = Model.set_number
    elif hasattr(Model, 'raffle_number'):
        number_field = Model.raffle_number
    elif hasattr(Model, 'manager_number'):
        number_field = Model.manager_number
    else:
        raise ValueError(f"Model {Model.__name__} doesn't have a recognized number field")

    # Build query
    query = db.query(func.max(number_field)).filter(getattr(Model, "entity_id") == entity_id)

    # Apply additional filters if provided
    if filters:
        for field_name, value in filters.items():
            if hasattr(Model, field_name):
                query = query.filter(getattr(Model, field_name) == value)

    last_number = query.scalar()
    return (last_number or 0) + 1


def get_record_by_composite_key(db: Session, Model, entity_id: int, **kwargs):
    """Universal function to get a record using composite primary key"""
    query = db.query(Model).filter(getattr(Model, "entity_id") == entity_id)

    for key, value in kwargs.items():
        if hasattr(Model, key):
            query = query.filter(getattr(Model, key) == value)

    record = query.first()
    if not record:
        raise HTTPException(status_code=404, detail=f"{Model.__name__} not found")

    return record


def get_records_filtered(db: Session, Model, entity_id: int, filters: Optional[Dict[str, Any]] = None,
                        limit: int = 0, offset: int = 0):
    """Universal function to get multiple records with filtering"""
    query = db.query(Model).filter(getattr(Model, "entity_id") == entity_id)

    # Apply filters
    if filters:
        for field_name, value in filters.items():
            if value is not None and hasattr(Model, field_name):
                query = query.filter(getattr(Model, field_name) == value)

    # Apply ordering based on model type
    if hasattr(Model, 'buyer_number'):
        query = query.order_by(Model.buyer_number)
    elif hasattr(Model, 'manager_number'):
        query = query.order_by(Model.manager_number)
    elif hasattr(Model, 'project_number'):
        if hasattr(Model, 'set_number'):
            query = query.order_by(Model.project_number, Model.set_number)
        elif hasattr(Model, 'raffle_number'):
            query = query.order_by(Model.project_number, Model.raffle_number)
        else:
            query = query.order_by(Model.project_number)

    # Apply pagination
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)

    return query.all()


def create_record(db: Session, new_record):
    """Universal create function"""
    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Record already exists or violates constraints")


def update_record_by_composite_key(db: Session, Model, entity_id: int, updates: Dict[str, Any], **pk_fields):
    """Universal update function using composite primary key"""
    # Get the record
    record = get_record_by_composite_key(db, Model, entity_id, **pk_fields)

    # Update fields (excluding PK fields)
    pk_field_names = set(pk_fields.keys())
    for field, value in updates.items():
        if field not in pk_field_names and hasattr(record, field):
            setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record, entity_id: int):
    """Universal delete function with entity validation"""
    if hasattr(record, 'entity_id') and entity_id != record.entity_id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this record")

    try:
        db.delete(record)
        db.commit()
        return {"message": "Record deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Record cannot be deleted. Error: {str(e)}")


# Specific helper functions using the universal ones
def get_next_buyer_number(db: Session, entity_id: int) -> int:
    """Get next buyer number for an entity"""
    from models.buyer import Buyer
    return get_next_number(db, Buyer, entity_id)


def get_next_project_number(db: Session, entity_id: int) -> int:
    """Get next project number for an entity"""
    from models.project import Project
    return get_next_number(db, Project, entity_id)


def get_next_set_number(db: Session, entity_id: int, project_number: int) -> int:
    """Get next set number for a project"""
    from models.raffleset import RaffleSet
    return get_next_number(db, RaffleSet, entity_id, {'project_number': project_number})


def get_next_raffle_number(db: Session, entity_id: int, project_number: int) -> int:
    """Get next raffle number for a project"""
    from models.raffle import Raffle
    return get_next_number(db, Raffle, entity_id, {'project_number': project_number})


def get_next_manager_number(db: Session, entity_id: int) -> int:
    """Get next manager number for an entity"""
    from models.manager import Manager
    return get_next_number(db, Manager, entity_id)


def get_buyer_by_name_phone(db: Session, name: str, phone: str, entity_id: int):
    """Find buyer by unique name-phone combination"""
    from models.buyer import Buyer
    buyer = db.query(Buyer).filter(
        Buyer.entity_id == entity_id,
        Buyer.name == name,
        Buyer.phone == phone
    ).first()

    if not buyer:
        raise HTTPException(status_code=404, detail=f"Buyer with name '{name}' and phone '{phone}' not found")

    return buyer
