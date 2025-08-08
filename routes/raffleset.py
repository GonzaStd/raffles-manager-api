from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from routes import get_record, get_records, create_record, update_record
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate

router = APIRouter()


@router.post("/raffleset")
def create_raffleset(
    raffleset: RaffleSetCreate,
    db: Session = Depends(get_db)
):
    # Find the last raffle number for this specific project (across all sets)
    last_number = (
        db.query(Raffle.number)
        .join(RaffleSet)
        .filter(RaffleSet.project_id == raffleset.project_id)
        .order_by(Raffle.number.desc())
        .limit(1)
        .scalar()
    )

    start = (last_number or 0) + 1
    end = start + raffleset.requested_count - 1

    new_raffleset = RaffleSet(
        project_id=raffleset.project_id,
        name=raffleset.name,
        type=raffleset.type,
        unit_price=raffleset.unit_price,
        init=start,
        final=end
    )

    create_record(db, new_raffleset)

    raffles = [
        Raffle(
            number=n,
            set_id=new_raffleset.id,
            state="available"
        )
        for n in range(start, end + 1)
    ]
    db.bulk_save_objects(raffles)
    db.commit()

    return {
        "message": "RaffleSet and Raffles created",
        "raffleset": {
            "id": new_raffleset.id,
            "name": new_raffleset.name,
            "type": new_raffleset.type,
            "init": new_raffleset.init,
            "final": new_raffleset.final,
            "unit_price": new_raffleset.unit_price,
            "project_id": new_raffleset.project_id
        },
        "range": f"{start}-{end}"
    }


@router.get("/raffleset/{id}")
def get_raffleset(
    id: int,
    db: Session = Depends(get_db)
):
    return get_record(db, RaffleSet, id, "Raffle Set")

@router.get("/rafflesets")
def get_rafflesets(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    return get_records(db, RaffleSet, limit)


@router.patch("/raffleset/{id}")
@router.put("/raffleset/{id}")
def update_raffleset(
    updates: RaffleSetUpdate,
    db: Session = Depends(get_db)
):
    return update_record(db, RaffleSet, updates)


@router.delete("/raffleset/{id}")
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
        raise HTTPException(
            status_code=400,
            detail="RaffleSet cannot be deleted. Error: " + str(e)
        )
    return {"message": "RaffleSet and its raffles deleted successfully"}
