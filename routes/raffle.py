from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.raffle import Raffle
from models.users import User
from models import RaffleSet, Project
from routes import get_record, get_records, update_record
from schemas.raffle import RaffleUpdate, RafflePayment
from auth.services.auth_service import get_current_active_user

router = APIRouter()


@router.get("/raffle")
def get_raffle(
    number: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffle = get_record(db, Raffle, number, "Raffle", id_field="number")
    # Verificar que la rifa pertenece a un proyecto del usuario
    raffleset = get_record(db, RaffleSet, raffle.set_id, "Raffle Set")
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")
    return raffle


@router.get("/raffles")
def get_raffles(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_records(db, Raffle, limit, offset)


@router.post("/raffle/pay")
def pay_raffle(
    payment: RafflePayment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffle_record = get_record(db, Raffle, payment.number, "Raffle", id_field="number")

    # Verificar que la rifa pertenece a un proyecto del usuario
    raffleset = get_record(db, RaffleSet, raffle_record.set_id, "Raffle Set")
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")

    if raffle_record.state not in ["available", "reserved"]:
        raise HTTPException(status_code=400, detail="Raffle is not available for payment")

    raffle_record.buyer_id = payment.buyer_id
    raffle_record.payment_method = payment.payment_method
    raffle_record.state = payment.state
    raffle_record.sell_date = datetime.now()

    db.commit()
    db.refresh(raffle_record)

    return raffle_record


@router.patch("/raffle")
def update_raffle(
    updates: RaffleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffle = get_record(db, Raffle, updates.number, "Raffle", id_field="number")
    raffleset = get_record(db, RaffleSet, raffle.set_id, "Raffle Set")
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")
    return update_record(db, Raffle, updates, id_field="number")
