from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.raffle import Raffle
from routes import get_record
from schemas.raffle import RaffleUpdate, RafflePayment

router = APIRouter()


@router.get("/raffle")
def get_raffle(
    number: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):
    raffle_record = get_record(db, Raffle, number, "Raffle")


@router.get("/raffles")
def get_raffles(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    if limit > 0:
        return db.query(Raffle).limit(limit).all()
    elif limit == 0:
        return db.query(Raffle).all()
    else:
        raise HTTPException(
            status_code=400,
            detail="Limit must be a non-negative integer."
        )


@router.post("/raffle/pay")
def pay_raffle(
    payment: RafflePayment,
    db: Session = Depends(get_db)
):
    raffle_record = get_record(db, Raffle, payment.number, "Raffle") #db.query(Raffle).filter(Raffle.number == payment.number).first()

    if raffle_record.state != "available":
        raise HTTPException(status_code=400, detail="Raffle is not available for payment")

    raffle_record.buyer_id = payment.buyer_id
    raffle_record.payment_method = payment.payment_method
    raffle_record.state = payment.state
    raffle_record.sell_date = datetime.now()

    db.commit()
    db.refresh(raffle_record)
    return raffle_record


@router.patch("/raffle")
@router.put("/raffle") # PUT should be used for fully updates, but I will use it like PATCH for compatibility.
def update_raffle(
    updates: RaffleUpdate,
    db: Session = Depends(get_db)
):
    raffle_record = get_record(db, Raffle, updates.number, "Raffle") #db.query(Raffle).filter(Raffle.number == updates.number).first()

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(raffle_record, field, value)

    db.commit()
    db.refresh(raffle_record)
    return raffle_record
