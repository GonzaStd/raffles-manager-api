from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from models.project import Project
from routes import get_record, get_records
from schemas.project import ProjectCreate, ProjectUpdate

router = APIRouter()


@router.post("/project")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(
        name=project.name,
        description=project.description,
        user_id=1  # TODO: Replace with actual user ID from authentication
    )
    
    db.add(new_project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="There's already a project with that name."
        )
    
    db.refresh(new_project)
    return new_project


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
    project_record = get_record(db, Project, updates.id, "Project")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(project_record, field, value)
    
    db.commit()
    db.refresh(project_record)
    return project_record


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

    db.delete(project_record)
    db.commit()
    return {"message": "Project, rafflesets and raffles associated with it, deleted successfully"}