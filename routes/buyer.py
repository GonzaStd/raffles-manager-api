from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.connection import get_db
from models.buyer import Buyer
from schemas.buyer import BuyerCreate, BuyerDelete, BuyerUpdate

router = APIRouter()

@router.post("/buyer")
def create_buyer(buyer: BuyerCreate, db: Session = Depends(get_db)):
    new_buyer = Buyer(
        name=buyer.name,
        phone=buyer.phone,
        email=str(buyer.email)
    )

    db.add(new_buyer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, # Bad Request
            detail="There's already a buyer with that name and phone."
        )

    db.refresh(new_buyer)

    return {
        "id": new_buyer.id,
        "name": new_buyer.name,
        "email": new_buyer.email,
        "phone": new_buyer.phone
    }

@router.delete("/buyer")
def delete_buyer(buyer: BuyerDelete, db: Session = Depends(get_db)):
    if buyer.id:
        buyer_record = db.query(Buyer).filter(Buyer.id == buyer.id).first()
        if buyer_record:
            db.delete(buyer_record)
            db.commit()
            return True
        else:
            raise HTTPException(
                status_code=400,  # Bad Request
                detail=f"There isn't any buyer with {buyer.id} id number."
            )
    else:
        buyer_record = db.query(Buyer).filter((Buyer.name == buyer.name) & (Buyer.phone == buyer.phone)).first()
        if buyer_record:
            db.delete(buyer_record)
            db.commit()
            return True
        else:
            raise HTTPException(
                status_code=400,  # Bad Request
                detail=f"There isn't any buyer with that pair of name and number."
            )

@router.get("/buyer")
def get_one_buyer(
        id: int = Query(..., ge=0),
        db: Session = Depends(get_db)
):
    buyer_record = db.query(Buyer).filter(Buyer.id == id).first()
    return buyer_record

@router.patch("/buyer")
def modify_buyer(
        updates: BuyerUpdate,
        id: int = Query(..., ge=0),
        db: Session = Depends(get_db)
):
    buyer = db.query(Buyer).filter(Buyer.id == id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(buyer, field, value)

    db.commit()
    db.refresh(buyer)
    return buyer


@router.get("/buyers")
def get_all_buyers(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    if limit > 0:
        return db.query(Buyer).limit(limit).all()
    else:
        return db.query(Buyer).all()
