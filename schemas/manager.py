from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional

class ManagerCreate(BaseModel):
    """Schema for creating a new manager"""
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=6)

class ManagerUpdate(BaseModel):
    """Schema for updating a manager"""
    manager_number: int = Field(..., ge=1)
    username: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.username, self.is_active]):
            raise ValueError("You must modify/update at least one value.")
        return self

class ManagerLogin(BaseModel):
    """Schema for manager login"""
    entity_name: str = Field(..., max_length=100, description="Name of the entity (organization)")
    username: str = Field(..., max_length=50, description="Manager username")
    password: str = Field(..., min_length=6, description="Manager password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "entity_name": "AcmeCorp",
                "username": "manager1",
                "password": "yourpassword"
            }
        }
    }

class ManagerResponse(BaseModel):
    """Schema for manager response"""
    entity_id: int
    manager_number: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
