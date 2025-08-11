from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.buyer import Buyer
from models.users import User
from routes import get_record, get_records, create_record, update_record, delete_record
from schemas.buyer import BuyerCreate, BuyerDelete, BuyerUpdate
from auth.services.auth_service import get_current_active_user

router = APIRouter()


@router.post("/buyer")
def create_buyer(
    buyer: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Los buyers no necesitan user_id si son compartidos entre usuarios
    # Si quieres que cada usuario tenga sus propios buyers, agrega user_id al modelo Buyer
    new_buyer = Buyer(
        name=buyer.name,
        phone=buyer.phone,
        email=str(buyer.email)
    )
    return create_record(db, new_buyer)


@router.get("/buyer")
def get_buyer(
    id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Los buyers pueden ser accedidos por cualquier usuario autenticado
    # Si quieres restricción por usuario, necesitas agregar user_id al modelo Buyer
    return get_record(db, Buyer, id, "Buyer")


@router.get("/buyers")
def get_buyers(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Todos los buyers disponibles para cualquier usuario autenticado
    query = db.query(Buyer)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


@router.patch("/buyer")
def update_buyer(
    buyer: BuyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Cualquier usuario autenticado puede actualizar buyers
    return update_record(db, Buyer, buyer)


@router.delete("/buyer")
def delete_buyer(
    buyer: BuyerDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get the buyer record first
    if buyer.id:
        buyer_record = get_record(db, Buyer, buyer.id, "Buyer")
    else:
        # Find by name and phone if id not provided
        buyer_record = db.query(Buyer).filter(
            Buyer.name == buyer.name,
            Buyer.phone == buyer.phone
        ).first()
        if not buyer_record:
            raise HTTPException(status_code=404, detail="Buyer not found")

    return delete_record(db, buyer_record)
