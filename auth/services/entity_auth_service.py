from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database.connection import get_db
from models.entity import Entity
from models.manager import Manager
from auth.utils import ALGORITHM, verify_password, SECRET_KEY
from auth.models.token import TokenData
from core.config_loader import settings
from datetime import datetime, timedelta
from typing import Optional, Union

bearer_scheme = HTTPBearer()


def get_entity(db: Session, name: str):
    """Get entity by name"""
    return db.query(Entity).filter(Entity.name == name).first()


def get_entity_by_id(db: Session, entity_id: int):
    """Get entity by ID"""
    return db.query(Entity).filter(Entity.id == entity_id).first()


def get_manager(db: Session, username: str):
    """Get manager by username (globally unique)"""
    return db.query(Manager).filter(Manager.username == username).first()


def get_manager_by_composite_key(db: Session, entity_id: int, manager_number: int):
    """Get manager by composite key"""
    return db.query(Manager).filter(
        Manager.entity_id == entity_id,
        Manager.manager_number == manager_number
    ).first()


def get_manager_by_entity_and_username(db: Session, entity_id: int, username: str):
    """Get manager by entity_id and username (multi-tenant)"""
    return db.query(Manager).filter(
        Manager.entity_id == entity_id,
        Manager.username == username
    ).first()


def authenticate_entity(db: Session, name: str, password: str):
    """Authenticate entity by name and password"""
    entity = get_entity(db, name)
    if not entity:
        return False
    if not verify_password(password, str(entity.hashed_password)):
        return False
    return entity


def authenticate_manager(db: Session, username: str, password: str):
    """Authenticate manager by username and password"""
    manager = get_manager(db, username)
    if not manager:
        return False
    if not verify_password(password, str(manager.hashed_password)):
        return False
    return manager


def authenticate_manager_by_entity(db: Session, entity_id: int, username: str, password: str):
    """Authenticate manager by entity_id, username, and password"""
    manager = get_manager_by_entity_and_username(db, entity_id, username)
    if not manager:
        return False
    if not verify_password(password, str(manager.hashed_password)):
        return False
    return manager


def create_access_token(subject: str, subject_type: str, entity_id: Optional[int] = None, expires_delta: Optional[timedelta] = None):
    """Create JWT access token with subject type (entity or manager)"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": subject_type  # "entity" or "manager"
    }
    if subject_type == "manager" and entity_id is not None:
        to_encode["entity_id"] = entity_id
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        subject_type: str = payload.get("type")
        entity_id: Optional[int] = payload.get("entity_id")
        if subject is None or subject_type is None:
            raise credentials_exception
        token_data = TokenData(username=subject)
        return token_data, subject_type, entity_id
    except JWTError:
        raise credentials_exception


def get_current_entity(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get current entity from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data, subject_type = verify_token(token.credentials, credentials_exception)

    if subject_type != "entity":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Entity access required"
        )

    entity = get_entity(db, name=token_data.username)
    if entity is None:
        raise credentials_exception
    return entity


def get_current_manager(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get current manager from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data, subject_type, entity_id = verify_token(token.credentials, credentials_exception)

    if subject_type != "manager" or entity_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    manager = get_manager_by_entity_and_username(db, entity_id, token_data.username)
    if manager is None:
        raise credentials_exception
    return manager


def get_current_entity_or_manager(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get current entity or manager from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data, subject_type, entity_id = verify_token(token.credentials, credentials_exception)

    if subject_type == "entity":
        entity = get_entity(db, name=token_data.username)
        if entity is None:
            raise credentials_exception
        return entity, "entity"
    elif subject_type == "manager" and entity_id is not None:
        manager = get_manager_by_entity_and_username(db, entity_id, token_data.username)
        if manager is None:
            raise credentials_exception
        return manager, "manager"
    else:
        raise credentials_exception



def get_current_active_manager(current_manager: Manager = Depends(get_current_manager)):
    """Get current active manager"""
    if not current_manager.is_active:
        raise HTTPException(status_code=400, detail="Inactive manager")
    return current_manager
