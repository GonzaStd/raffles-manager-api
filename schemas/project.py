from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    """Schema para crear un nuevo proyecto"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field("", max_length=500)

class ProjectUpdate(BaseModel):
    """Schema para actualizar un proyecto existente"""
    id: int = Field(..., ge=1)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.name, self.description]):
            raise ValueError("You must modify/update at least one value.")
        return self

class ProjectResponse(BaseModel):
    """Schema de respuesta para proyectos"""
    id: int
    name: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
