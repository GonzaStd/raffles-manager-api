from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models import RaffleSet, Raffle
from models.project import Project
from models.users import User
from routes import get_record, get_records, create_record, update_record, delete_record
from schemas.project import ProjectCreate, ProjectUpdate, ProjectDelete
from auth.services.auth_service import get_current_active_user

router = APIRouter()


@router.post("/project")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # We need to use it so only current user can create record
):
    new_project = Project(
        name=project.name,
        description=project.description,
        user_id=current_user.id
    )
    return create_record(db, new_project)


@router.get("/project")
def get_project(
    id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # We need to use it so only current user can get record
):
    return get_record(db, Project, id, "Project")

@router.get("/projects")
def get_projects(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_records(db, Project, limit, offset)


@router.patch("/project")
def update_project(
    updates: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verificar que el proyecto pertenece al usuario antes de actualizar
    existing_project = get_record(db, Project, updates.id, "Project")
    if existing_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")
    return update_record(db, Project, updates)


@router.delete("/project")
def delete_project(
    project_data: ProjectDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project_record = get_record(db, Project, project_data.id, "Project")

    if project_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: not your project")

    # Delete rafflesets and raffles associated with the project
    rafflesets = db.query(RaffleSet).filter(RaffleSet.project_id == project_data.id).all()
    sets_ids = [set.id for set in rafflesets]

    for set_id in sets_ids:
        db.query(Raffle).filter(Raffle.set_id == set_id).delete()

    for raffleset in rafflesets:
        db.delete(raffleset)

    return delete_record(db, project_record)
