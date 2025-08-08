from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from models.project import Project
from routes import get_record, get_records, create_record, update_record, delete_record
from schemas.project import ProjectCreate, ProjectUpdate

router = APIRouter()


@router.post("/project")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(
        name=project.name,
        description=project.description,
        user_id=1  # TODO: Replace with actual user ID from authentication
    )
    return create_record(db, new_project)


@router.get("/project")
def get_project(
    id: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):
    return get_record(db, Project, id, "Project")

@router.get("/projects")
def get_projects(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    return get_records(db, Project, limit)


@router.patch("/project")
@router.put("/project")
def update_project(
    updates: ProjectUpdate,
    db: Session = Depends(get_db)
):
    return update_record(db, Project, updates)


@router.delete("/project")
def delete_project(
    id: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):
    project_record = get_record(db, Project, id, "Project")

    # Delete rafflesets and raffles associated with the project
    rafflesets = db.query(RaffleSet).filter(RaffleSet.project_id == id).all()
    sets_ids = [set.id for set in rafflesets]

    for set_id in sets_ids:
        db.query(Raffle).filter(Raffle.set_id == set_id).delete()

    for raffleset in rafflesets:
        db.delete(raffleset)

    return delete_record(db, project_record)