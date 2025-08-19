from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.entity import Entity
from models.raffleset import RaffleSet
from models.raffle import Raffle
from models.project import Project
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate, RaffleSetResponse
from routes import (get_records_filtered, create_record, update_record_by_composite_key, delete_record,
                   get_record_by_composite_key, get_next_set_number, get_next_raffle_number)
from typing import List
from auth.services.entity_auth_service import get_current_entity

router = APIRouter()

@router.post("/project/{project_number}/raffleset", response_model=RaffleSetResponse)
def create_raffle_set(
    project_number: int = Path(..., ge=1),
    raffle_set: RaffleSetCreate = ...,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Create a new raffle set and its associated raffles."""
    # Verify that the project belongs to the entity
    get_record_by_composite_key(db, Project, current_entity.id, project_number=project_number)

    # Get next set number for this project
    set_number = get_next_set_number(db, current_entity.id, project_number)

    # Calculate init and final based on existing raffles in this project
    last_raffle_number = get_next_raffle_number(db, current_entity.id, project_number) - 1
    init_number = last_raffle_number + 1
    final_number = init_number + raffle_set.quantity - 1

    # Create the raffle set
    new_raffle_set = RaffleSet(
        entity_id=current_entity.id,
        project_number=project_number,
        set_number=set_number,
        name=raffle_set.name,
        type=raffle_set.type,
        init=init_number,
        final=final_number,
        unit_price=raffle_set.unit_price
    )

    created_set = create_record(db, new_raffle_set)

    # Create individual raffles for this set
    for raffle_num in range(init_number, final_number + 1):
        new_raffle = Raffle(
            entity_id=current_entity.id,
            project_number=project_number,
            raffle_number=raffle_num,
            set_number=set_number,
            state="available"
        )
        db.add(new_raffle)

    db.commit()
    return created_set

@router.get("/project/{project_number}/raffleset/{set_number}", response_model=RaffleSetResponse)
def get_raffle_set(
    project_number: int = Path(..., ge=1),
    set_number: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Get a specific raffle set by project and set number."""
    return get_record_by_composite_key(db, RaffleSet, current_entity.id,
                                      project_number=project_number, set_number=set_number)

@router.get("/project/{project_number}/rafflesets", response_model=List[RaffleSetResponse])
def get_raffle_sets_by_project(
    project_number: int = Path(..., ge=1),
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Get all raffle sets for a specific project."""
    # Verify project belongs to entity
    get_record_by_composite_key(db, Project, current_entity.id, project_number=project_number)

    # Get raffle sets with project filter
    return get_records_filtered(db, RaffleSet, current_entity.id,
                               {"project_number": project_number}, limit, offset)

@router.put("/project/{project_number}/raffleset", response_model=RaffleSetResponse)
def update_raffle_set(
    project_number: int = Path(..., ge=1),
    raffle_set_update: RaffleSetUpdate = ...,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Update an existing raffle set."""
    pk_fields = {'project_number': project_number, 'set_number': raffle_set_update.set_number}
    updates = {k: v for k, v in raffle_set_update.model_dump(exclude_unset=True).items()
               if k not in {'project_number', 'set_number'}}
    return update_record_by_composite_key(db, RaffleSet, current_entity.id, updates, **pk_fields)

@router.delete("/project/{project_number}/raffleset/{set_number}")
def delete_raffle_set(
    project_number: int = Path(..., ge=1),
    set_number: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Delete a raffle set and all its associated raffles."""
    raffle_set = get_record_by_composite_key(db, RaffleSet, current_entity.id,
                                            project_number=project_number, set_number=set_number)
    return delete_record(db, raffle_set, current_entity.id)
