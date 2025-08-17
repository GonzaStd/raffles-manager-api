from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from datetime import datetime

class RaffleCreate(BaseModel):
    """Schema para crear una nueva rifa"""
    number: int = Field(..., ge=1)
    set_id: int = Field(..., ge=1)
    state: Literal["available", "sold", "reserved"] = "available"
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None

class RaffleUpdate(BaseModel):
    """Schema para actualizar una rifa existente"""
    number: int = Field(..., ge=1)  # Agregué number para identificar la rifa
    state: Optional[Literal["available", "sold", "reserved"]] = None
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    buyer_id: Optional[int] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.state, self.payment_method, self.buyer_id]):
            raise ValueError("You must modify/update at least one value.")
        return self

class RaffleSell(BaseModel):
    """Schema para vender una rifa"""
    buyer_id: int = Field(..., ge=1)
    payment_method: Literal["cash", "card", "transfer"]

class RaffleFilters(BaseModel):
    """Schema for filtering raffles - used in POST /raffles"""
    project_id: int = Field(..., ge=1, description="Project ID is required - raffles are organized by project")
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    state: Optional[Literal["available", "sold", "reserved"]] = None
    set_id: Optional[int] = Field(None, ge=1)
    limit: int = Field(0, ge=0)
    offset: int = Field(0, ge=0)

class RaffleResponse(BaseModel):
    """Schema de respuesta para rifas"""
    number: int
    set_id: int
    buyer_id: Optional[int]
    user_id: int
    payment_method: Optional[str]
    state: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
