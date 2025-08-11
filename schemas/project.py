from pydantic import BaseModel, Field, model_validator
from typing import Optional

class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=60)
    description: Optional[str] = None

class ProjectDelete(BaseModel):
    id: int = Field(..., ge=1),

class ProjectUpdate(BaseModel):
    id: int = Field(..., ge=1),
    name: Optional[str] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        name, description = (self.name, self.description)
        if name is None and description is None:
            raise ValueError("You must modify/update at least one value.")
        return self