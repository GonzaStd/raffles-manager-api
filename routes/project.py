from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models.users import User
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from routes import (get_records, create_record, update_record, delete_record,
                   get_record_by_composite_key, get_next_project_number)
from typing import List

router = APIRouter()


@router.post("/project", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo proyecto con auto-increment per user."""
    project_number = get_next_project_number(db, current_user.id)

    new_project = Project(
        user_id=current_user.id,
        project_number=project_number,
        name=project.name,
        description=project.description
    )
    return create_record(db, new_project)


@router.get("/project/{project_number}", response_model=ProjectResponse)
def get_project(
    project_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un proyecto específico por su número."""
    return get_record_by_composite_key(db, Project, current_user.id, project_number=project_number)


@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los proyectos del usuario."""
    return get_records(db, Project, current_user, limit, offset)


@router.put("/project", response_model=ProjectResponse)
def update_project(
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un proyecto existente."""
    return update_record(db, Project, project_update, current_user)


@router.delete("/project/{project_number}")
def delete_project(
    project_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un proyecto y todos sus sets/rifas asociados."""
    project = get_record_by_composite_key(db, Project, current_user.id, project_number=project_number)
    return delete_record(db, project, current_user)
