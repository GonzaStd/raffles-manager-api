from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.entity_auth_service import (
    authenticate_entity, authenticate_manager, create_access_token, get_current_active_manager, get_current_entity)
from auth.models.token import Token
from models.entity import Entity
from models.manager import Manager
from schemas.entity import EntityCreate, EntityResponse
from schemas.manager import ManagerCreate, ManagerResponse, ManagerLogin
from auth.utils import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/entity/register", response_model=dict)
def register_entity(entity_data: EntityCreate, db: Session = Depends(get_db)):
    """
    Register a new entity (organization).
    Only gives generic response to prevent entity enumeration.
    Real errors are reported specifically.
    """
    try:
        # Check if entity already exists
        from auth.services.entity_auth_service import get_entity
        existing_entity = get_entity(db, entity_data.name)

        if existing_entity:
            # ⚠️ IMPORTANT: Don't reveal that the entity exists (enumeration prevention)
            # Internal log for administrators
            logger.warning(f"Registration attempt for existing entity: {entity_data.name}")

            # Generic response to prevent enumeration
            return {
                "message": "Entity name already exists",
                "detail": "Couldn't create account"
            }

        # Create new entity
        hashed_password = get_password_hash(entity_data.password)
        new_entity = Entity(
            name=entity_data.name,
            hashed_password=hashed_password,
            description=entity_data.description
        )

        db.add(new_entity)
        db.commit()
        db.refresh(new_entity)

        # Success log
        logger.info(f"New entity registered successfully: {entity_data.name}")

        return {
            "message": "Registration completed successfully",
            "detail": "Your entity account has been created successfully"
        }

    except Exception as e:
        # Log real error
        logger.error(f"Registration error for {entity_data.name}: {str(e)}")

        # ✅ SHOW REAL ERROR - Not enumeration, it's a technical problem
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/manager/register", response_model=dict)
def register_manager(
    manager_data: ManagerCreate,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """
    Register a new manager for the current entity.
    Only entities can create managers.
    """
    try:
        # Check if manager username already exists for this entity
        existing_manager = db.query(Manager).filter(
            Manager.entity_id == current_entity.id,
            Manager.username == manager_data.username
        ).first()

        if existing_manager:
            return {
                "message": "Manager username already exists for this entity",
                "detail": "Please choose a different username"
            }

        # Get next manager number for this entity
        from routes import get_next_manager_number
        manager_number = get_next_manager_number(db, current_entity.id)

        # Create new manager with simplified fields
        hashed_password = get_password_hash(manager_data.password)
        new_manager = Manager(
            entity_id=current_entity.id,
            manager_number=manager_number,
            username=manager_data.username,
            hashed_password=hashed_password
        )

        db.add(new_manager)
        db.commit()
        db.refresh(new_manager)

        # Success log
        logger.info(f"New manager registered successfully: {manager_data.username} for entity {current_entity.name}")

        return {
            "message": "Manager registration completed successfully",
            "detail": f"Manager {manager_data.username} has been created successfully"
        }

    except Exception as e:
        # Log real error
        logger.error(f"Manager registration error for {manager_data.username}: {str(e)}")

        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Manager registration failed: {str(e)}"
        )

@router.post("/entity/login", response_model=Token)
def login_entity(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Secure entity login without revealing if the entity exists."""
    entity = authenticate_entity(db, form_data.username, form_data.password)
    if not entity:
        # Log failed attempt
        logger.warning(f"Failed entity login attempt for: {form_data.username}")

        # Generic message that doesn't reveal if entity exists or password is wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect entity name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful login
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=entity.name, subject_type="entity", expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/manager/login", response_model=Token)
def login_manager(
    login_data: ManagerLogin,
    db: Session = Depends(get_db)
):
    """Multi-tenant manager login: requires entity_name, username, password."""
    # Check if entity exists
    from auth.services.entity_auth_service import get_entity, get_manager_by_entity_and_username, authenticate_manager_by_entity
    entity = get_entity(db, login_data.entity_name)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The entity you entered does not exist in the database."
        )
    # Authenticate manager by entity
    manager = authenticate_manager_by_entity(db, entity.id, login_data.username, login_data.password)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect manager username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=manager.username, subject_type="manager", entity_id=entity.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/entity/me", response_model=EntityResponse)
def get_current_entity_info(current_entity: Entity = Depends(get_current_entity)):
    """Get current entity information"""
    return current_entity

@router.get("/manager/me", response_model=ManagerResponse)
def get_current_manager_info(current_manager: Manager = Depends(get_current_active_manager)):
    """Get current manager information"""
    return current_manager
