from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.entity_auth_service import get_current_entity, get_current_entity_or_manager
from models.entity import Entity
from models.raffle import Raffle
from models.raffleset import RaffleSet
from models.buyer import Buyer
from models.project import Project
from models.manager import Manager
from schemas.raffle import RaffleUpdate, RaffleResponse, RaffleSell, RaffleFilters
from routes import get_record_by_composite_key, update_record_by_composite_key, get_records_filtered
from typing import List, Union

router = APIRouter()

@router.get("/project/{project_number}/raffle/{raffle_number}", response_model=RaffleResponse)
def get_raffle(
    project_number: int = Path(..., ge=1),
    raffle_number: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Get a specific raffle by its number within a project. Managers and entities can view any raffle."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    return get_record_by_composite_key(db, Raffle, entity_id, project_number=project_number, raffle_number=raffle_number)

@router.post("/project/{project_number}/raffles", response_model=List[RaffleResponse])
def get_raffles_filtered(
    project_number: int,
    filters: RaffleFilters,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Get raffles with specific filters. Managers and entities can view all raffles in their entity."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    # Verify that the project belongs to the entity
    get_record_by_composite_key(db, Project, entity_id, project_number=project_number)
    # Build filters dict from RaffleFilters, excluding None and pagination fields
    filter_dict = {k: v for k, v in filters.model_dump().items() if v is not None and k not in ["limit", "offset"]}
    filter_dict["project_number"] = project_number  # Always filter by project_number
    return get_records_filtered(db, Raffle, entity_id, filter_dict, filters.limit, filters.offset)

@router.put("/project/{project_number}/raffle", response_model=RaffleResponse)
def update_raffle(
    project_number: int,
    raffle_update: RaffleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Update an existing raffle. Managers can only update raffles they sold."""
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    raffle = get_record_by_composite_key(db, Raffle, entity_id, project_number=project_number, raffle_number=raffle_update.raffle_number)
    if user_type == "manager" and raffle.sold_by_manager_number != user.manager_number:
        raise HTTPException(status_code=403, detail="Managers can only update raffles they sold.")
    pk_fields = {'project_number': project_number, 'raffle_number': raffle_update.raffle_number}
    updates = {k: v for k, v in raffle_update.model_dump(exclude_unset=True).items()
               if k not in {'project_number', 'raffle_number'}}
    return update_record_by_composite_key(db, Raffle, entity_id, updates, **pk_fields)

@router.post("/project/{project_number}/raffle/{raffle_number}/sell", response_model=RaffleResponse)
def sell_raffle(
    project_number: int,
    raffle_number: int,
    sale_data: RaffleSell,
    db: Session = Depends(get_db)
):
    """
    Sell a raffle assigning it to a buyer.
    Can be called by either entities or managers.
    If called by a manager, it automatically tracks who made the sale.
    """
    # Get current user (entity or manager)
    current_user, user_type = get_current_entity_or_manager(db=db)

    if user_type == "entity":
        entity_id = current_user.id
        sold_by_manager_number = sale_data.sold_by_manager_number  # Manual assignment
    elif user_type == "manager":
        entity_id = current_user.entity_id
        sold_by_manager_number = current_user.manager_number  # Auto-track the selling manager
    else:
        raise HTTPException(status_code=403, detail="Invalid user type")

    # Verify that the raffle belongs to the entity
    raffle = get_record_by_composite_key(db, Raffle, entity_id,
                                        project_number=project_number, raffle_number=raffle_number)

    # Verify that the buyer belongs to the entity
    get_record_by_composite_key(db, Buyer, entity_id, buyer_number=sale_data.buyer_number)

    if raffle.state not in ["available", "reserved"]:
        raise HTTPException(status_code=400, detail="Raffle is not available for sale")

    # Update the raffle with sale data
    raffle.buyer_entity_id = entity_id
    raffle.buyer_number = sale_data.buyer_number
    raffle.payment_method = sale_data.payment_method
    raffle.state = "sold"

    # Track which manager made the sale
    if sold_by_manager_number:
        raffle.sold_by_entity_id = entity_id
        raffle.sold_by_manager_number = sold_by_manager_number

    db.commit()
    db.refresh(raffle)
    return raffle
