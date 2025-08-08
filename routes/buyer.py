from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.buyer import Buyer
from routes import get_record, get_records, create_record
from schemas.buyer import BuyerCreate, BuyerDelete, BuyerUpdate

router = APIRouter()


@router.post("/buyer")
def create_buyer(buyer: BuyerCreate, db: Session = Depends(get_db)):
    new_buyer = Buyer(
        name=buyer.name,
        phone=buyer.phone,
        email=str(buyer.email)
    )
    return create_record(db, new_buyer)


@router.get("/buyer")
def get_buyer(
    id: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):
    return get_record(db, Buyer, id, "Buyer")


@router.get("/buyers")
def get_buyers(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    return get_records(db, Buyer, limit)


@router.patch("/buyer")
@router.put("/buyer")
def update_buyer(
    updates: BuyerUpdate,
    db: Session = Depends(get_db)
):
    buyer_record = get_record(db, Buyer, updates.id, "Buyer")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(buyer_record, field, value)
    
    db.commit()
    db.refresh(buyer_record)
    return buyer_record


@router.delete("/buyer")
def delete_buyer(buyer: BuyerDelete, db: Session = Depends(get_db)):
    if buyer.id:
        buyer_record = get_record(db, Buyer, buyer.id, "Buyer")
        db.delete(buyer_record)
        db.commit()
        return {"message": "Buyer deleted successfully"}
    else:
        buyer_record = db.query(Buyer).filter(
            (Buyer.name == buyer.name) & (Buyer.phone == buyer.phone)
        ).first()
        if not buyer_record:
            raise HTTPException(
                status_code=404,
                detail="There isn't any buyer with that pair of name and number."
            )
        db.delete(buyer_record)
        db.commit()
        return {"message": "Buyer deleted successfully"}