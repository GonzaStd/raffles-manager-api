from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate

router = APIRouter()
@router.post("/raffleset")
def create_raffleset(
    raffleset: RaffleSetCreate,
    db: Session = Depends(get_db)
):
        # Buscar el último número global de todas las rifas (no por proyecto)
        last_number = db.query(Raffle).filter(Raffle.set_id == raffleset.project_id).order_by(Raffle.number.desc()).first()
        print("Last number:", last_number)
        start = (last_number or 0) + 1
        end = start + raffleset.requested_count - 1
        print("Start:", start, "\nEnd:", end)

        new_raffleset = RaffleSet(
            project_id=raffleset.project_id,
            name=raffleset.name,
            type=raffleset.type,
            unit_price=raffleset.unit_price,
            init=start,
            final=end
        )

        db.add(new_raffleset)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Raffle set already exists")
        db.refresh(new_raffleset)

        raffles = [
            Raffle(
                # number=n,  # ❌ NO asignar - es AUTO_INCREMENT
                set_id=new_raffleset.id,
                state="available"
            )
            for n in range(start, end + 1)  # Solo para contar cuántos crear
        ]
        db.bulk_save_objects(raffles)
        db.commit()

        return {"message": "RaffleSet and Raffles created", "raffle_set_id": new_raffleset.id, "range": f"{start}-{end}"}

@router.get("/raffleset")
def get_raffleset(
    id: int,
    db: Session = Depends(get_db)
):
    raffleset = db.query(RaffleSet).filter(RaffleSet.id == id).first()
    if not raffleset:
        raise HTTPException(status_code=404, detail="RaffleSet not found")
    return raffleset

@router.get("/rafflesets")
def get_rafflesets(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    if limit > 0:
        return db.query(RaffleSet).limit(limit).all()
    elif limit == 0:
        return db.query(RaffleSet).all()
    else:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Limit must be a non-negative integer."
        )
@router.patch("/raffleset")
def update_raffleset(
    id: int,
    updates: RaffleSetUpdate,
    db: Session = Depends(get_db)
):
    raffleset_record = db.query(RaffleSet).filter(RaffleSet.id == id).first()

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(raffleset_record, field, value)
    db.commit()
    db.refresh(raffleset_record)
    return raffleset_record


@router.delete("/raffleset")
def delete_raffleset(
    id: int,
    db: Session = Depends(get_db)
):

    raffleset_record = db.query(RaffleSet).filter(RaffleSet.id == id).first()

    if not raffleset_record:
        raise HTTPException(status_code=404, detail="RaffleSet not found")

    db.query(Raffle).filter(Raffle.set_id == id).delete()
    db.delete(raffleset_record)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="RaffleSet cannot be deleted. Error: " + str(e))
    return {"message": "RaffleSet and its raffles, deleted successfully"}