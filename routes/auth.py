from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import authenticate_user, create_access_token, get_current_active_user, get_user
from auth.models.token import Token
from models.users import User
from schemas.users import UserCreate, UserResponse
from auth.utils import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=dict)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registro seguro de usuario.
    Solo da respuesta genérica para prevenir user enumeration.
    Errores reales se reportan específicamente.
    """
    try:
        # Verificar si el usuario ya existe
        existing_user = get_user(db, user_data.username)

        if existing_user:
            # ⚠️ IMPORTANTE: No revelar que el usuario existe (user enumeration prevention)
            # Log interno para administradores
            logger.warning(f"Registration attempt for existing username: {user_data.username}")

            # Respuesta genérica para prevenir user enumeration
            return {
                "message": "Registration completed successfully",
                "detail": "Your account has been created successfully"
            }

        # Crear nuevo usuario
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log exitoso
        logger.info(f"New user registered successfully: {user_data.username}")

        return {
            "message": "Registration completed successfully",
            "detail": "Your account has been created successfully"
        }

    except Exception as e:
        # Log del error real
        logger.error(f"Registration error for {user_data.username}: {str(e)}")

        # ✅ MOSTRAR ERROR REAL - No es user enumeration, es un problema técnico
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login seguro sin revelar si el usuario existe."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log del intento fallido
        logger.warning(f"Failed login attempt for username: {form_data.username}")

        # Mensaje genérico que no revela si el usuario existe o la contraseña está mal
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",  # ✅ Mensaje genérico
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log del login exitoso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)  # Quitado "/auth"
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user
