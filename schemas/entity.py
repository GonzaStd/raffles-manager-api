from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional

class EntityCreate(BaseModel):
    """Schema for creating a new entity"""
    name: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)
    description: Optional[str] = Field(None, max_length=500)

class EntityUpdate(BaseModel):
    """Schema for updating an entity"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.name, self.description]):
            raise ValueError("You must modify/update at least one value.")
        return self

class EntityResponse(BaseModel):
    """Schema for entity response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
