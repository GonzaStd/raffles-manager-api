from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.entity import Entity
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from routes import (get_records_filtered, create_record, update_record_by_composite_key, delete_record,
                   get_record_by_composite_key, get_next_project_number)
from typing import List
from auth.services.entity_auth_service import get_current_entity, get_current_entity_or_manager

router = APIRouter()


@router.post("/project", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Create a new project with auto-increment per entity."""
    project_number = get_next_project_number(db, current_entity.id)

    new_project = Project(
        entity_id=current_entity.id,
        project_number=project_number,
        name=project.name,
        description=project.description
    )
    return create_record(db, new_project)


@router.get("/project/{project_number}", response_model=ProjectResponse)
def get_project(
    project_number: int,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Get a specific project by its number."""
    return get_record_by_composite_key(db, Project, current_entity.id, project_number=project_number)


@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
    limit: int = 0,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_entity_or_manager)
):
    """Get all projects for the current entity or manager's entity."""
    # Determine user type
    if isinstance(current_user, tuple):
        user, user_type = current_user
    else:
        user = current_user
        user_type = "entity"
    entity_id = user.entity_id if user_type == "manager" else user.id
    return get_records_filtered(db, Project, entity_id, None, limit, offset)


@router.put("/project", response_model=ProjectResponse)
def update_project(
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Update an existing project."""
    pk_fields = {'project_number': project_update.project_number}
    updates = {k: v for k, v in project_update.model_dump(exclude_unset=True).items() if k != 'project_number'}
    return update_record_by_composite_key(db, Project, current_entity.id, updates, **pk_fields)


@router.delete("/project/{project_number}")
def delete_project(
    project_number: int,
    db: Session = Depends(get_db),
    current_entity: Entity = Depends(get_current_entity)
):
    """Delete a project and all its associated sets/raffles."""
    project = get_record_by_composite_key(db, Project, current_entity.id, project_number=project_number)
    return delete_record(db, project, current_entity.id)
