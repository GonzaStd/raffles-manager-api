from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.raffle import Raffle
from schemas.raffle import RaffleUpdate, RafflePayment

router = APIRouter()

@router.get("/raffle")
def get_raffle(
    number: int,
    db: Session = Depends(get_db)
):
    raffle = db.query(Raffle).filter(Raffle.number == number).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return raffle

@router.get("/raffles")
def get_raffles(
        limit: int = 0,
        db: Session = Depends(get_db)
):
    if limit < 0:
        raffles = db.query(Raffle).limit(limit).all()
        return raffles
    elif limit == 0:
        raffles = db.query(Raffle).all()
        return raffles
    else:
        raffles = db.query(Raffle).limit(limit).all()
        return raffles

@router.post("/raffle")
def pay_raffle(
    payment: RafflePayment,
    number: int,
    db: Session = Depends(get_db)
):
    raffle = db.query(Raffle).filter(Raffle.number == number).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")

    if raffle.state != "available":
        raise HTTPException(status_code=400, detail="Raffle is not available for payment")

    raffle.buyer_id = payment.buyer_id
    raffle.payment_method = payment.payment_method
    raffle.state = payment.state

    db.commit()
    db.refresh(raffle)
    return raffle
@router.patch("/raffle")
def update_raffle(
    updates: RaffleUpdate,
    set_id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    raffle = db.query(Raffle).filter(Raffle.set_id == set_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(raffle, field, value)

    db.commit()
    db.refresh(raffle)
    return raffle