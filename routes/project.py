from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.connection import get_db
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
