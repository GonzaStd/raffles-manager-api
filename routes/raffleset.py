from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle, Project
from models.users import User
from routes import get_record, get_records, create_record, update_record, delete_record
from schemas.raffleset import RaffleSetCreate, RaffleSetUpdate, RaffleSetDelete
from auth.services.auth_service import get_current_active_user

router = APIRouter()


@router.post("/raffleset")
def create_raffleset(
    raffleset: RaffleSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verificar que el proyecto pertenece al usuario
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffleset = get_record(db, RaffleSet, id, "Raffle Set")
    # Verificar que el raffleset pertenece a un proyecto del usuario
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")
    return raffleset


@router.get("/rafflesets")
def get_rafflesets(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_records(db, RaffleSet, limit, offset)


@router.patch("/raffleset")
def update_raffleset(
    updates: RaffleSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffleset = get_record(db, RaffleSet, updates.id, "Raffle Set")
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")
    return update_record(db, RaffleSet, updates)


@router.delete("/raffleset")
def delete_raffleset(
    raffleset_data: RaffleSetDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    raffleset = get_record(db, RaffleSet, raffleset_data.id, "Raffle Set")
    project = get_record(db, Project, raffleset.project_id, "Project")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")

    # Delete associated raffles first
    raffles = db.query(Raffle).filter(Raffle.set_id == raffleset_data.id).all()
    for raffle in raffles:
        db.delete(raffle)

    return delete_record(db, raffleset)
