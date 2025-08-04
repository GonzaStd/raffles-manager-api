from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate

router = APIRouter()

@router.post("/project")
def create_project(project:ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=project.name,
        description=project.description
    )
    db.add(project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="There's already a project with that name."
        )
    db.refresh(project)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description
    }

@router.put("/project")
def update_project(project:ProjectUpdate, db: Session = Depends(get_db)):
    project_record = db.query(Project).filter(Project.id == project.id).first()
    if not project_record:
        raise HTTPException(
            status_code=404,  # Not Found
            detail=f"There isn't any project with {project.id} id number."
        )

    if project.name:
        project_record.name = project.name
    if project.description:
        project_record.description = project.description

    db.commit()
    db.refresh(project_record)

    return {
        "id": project_record.id,
        "name": project_record.name,
        "description": project_record.description
    }

@router.get("/project")
def get_project(
    id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    project_record = db.query(Project).filter(Project.id == id).first()
    if not project_record:
        raise HTTPException(
            status_code=404,  # Not Found
            detail=f"There isn't any project with {id} id number."
        )
    return {
        "id": project_record.id,
        "name": project_record.name,
        "description": project_record.description
    }

@router.get("/projects")
def get_projects(
    limit: int = 0,
    db: Session = Depends(get_db)
):
    if limit > 0:
        projects = db.query(Project).limit(limit).all()
        return projects
    elif limit == 0:
        projects = db.query(Project).all()
        return projects
    else:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Limit must be a positive integer or zero."
        )

@router.delete("/project")
def delete_project(
    id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    project_record = db.query(Project).filter(Project.id == id).first()
    if not project_record:
        raise HTTPException(
            status_code=404,  # Not Found
            detail=f"There isn't any project with {id} id number."
        )
    # Delete rafflesets and raffles associated with the project
    raffles_set = db.query(RaffleSet).filter(RaffleSet.project_id == id).all()
    sets_ids = [set.id for set in raffles_set]
    for set_id in sets_ids:
        db.query(Raffle).filter(Raffle.set_id == set_id).delete()
    for set in raffles_set:
        db.delete(set)

    db.delete(project_record)
    db.commit()
    return {"detail": "Project, rafflesets and raffles associated with it, deleted successfully."}