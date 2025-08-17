from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from auth.services.auth_service import get_current_active_user
from models import RaffleSet, Raffle
from models.users import User
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from routes import get_record, get_records, create_record, update_record, delete_record
from typing import List

router = APIRouter()


@router.post("/project", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,  # Cambié ProjectBase por ProjectCreate
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo proyecto."""
    new_project = Project(
        name=project.name,
        description=project.description,
        user_id=current_user.id
    )
    return create_record(db, new_project)


@router.get("/project/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un proyecto específico."""
    return get_record(db, Project, project_id, current_user)


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


@router.delete("/project/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    # Delete rafflesets and raffles associated with the project
    rafflesets = db.query(RaffleSet).filter(RaffleSet.project_id == project_id).all()
    sets_ids = [raffleset.id for raffleset in rafflesets]

    for set_id in sets_ids:
        db.query(Raffle).filter(Raffle.set_id == set_id).delete()

    for raffleset in rafflesets:
        db.delete(raffleset)

    project = get_record(db, Project, project_id, current_user)
    return delete_record(db, project, current_user)
