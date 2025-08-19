from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Literal, Optional
from datetime import datetime


class RaffleSetCreate(BaseModel):
    """Schema for creating a new raffle set"""
    name: str = Field(..., max_length=60)
    project_number: int = Field(..., ge=1, description="Project number within entity's projects")
    type: Literal["online", "physical"]
    quantity: int = Field(..., ge=1, description="Number of raffles to create in this set")
    unit_price: int = Field(..., ge=1)

class RaffleSetUpdate(BaseModel):
    """Schema for updating an existing raffle set"""
    project_number: int = Field(..., ge=1)
    set_number: int = Field(..., ge=1)
    name: Optional[str] = Field(None, max_length=60)
    type: Optional[Literal["online", "physical"]] = None
    unit_price: Optional[int] = Field(None, ge=1)

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.name, self.type, self.unit_price]):
            raise ValueError("You must modify/update at least one value.")
        return self

class RaffleSetResponse(BaseModel):
    """Schema for raffle set response"""
    entity_id: int
    project_number: int
    set_number: int
    name: str
    type: str
    init: int  # Automatically calculated
    final: int  # Automatically calculated
    unit_price: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
