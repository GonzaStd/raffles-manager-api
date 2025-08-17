from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from datetime import datetime

class RaffleCreate(BaseModel):
    """Schema para crear una nueva rifa"""
    project_number: int = Field(..., ge=1)
    raffle_number: int = Field(..., ge=1)
    set_number: int = Field(..., ge=1)
    state: Literal["available", "sold", "reserved"] = "available"
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None

class RaffleUpdate(BaseModel):
    """Schema para actualizar una rifa existente"""
    project_number: int = Field(..., ge=1)
    raffle_number: int = Field(..., ge=1)  # Cambié de number a raffle_number
    state: Optional[Literal["available", "sold", "reserved"]] = None
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    buyer_number: Optional[int] = None  # Cambié de buyer_id a buyer_number

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.state, self.payment_method, self.buyer_number]):
            raise ValueError("You must modify/update at least one value.")
        return self

class RaffleSell(BaseModel):
    """Schema para vender una rifa"""
    buyer_number: int = Field(..., ge=1)  # Cambié de buyer_id a buyer_number
    payment_method: Literal["cash", "card", "transfer"]

class RaffleFilters(BaseModel):
    """Schema for filtering raffles - used in POST /raffles"""
    project_number: int = Field(..., ge=1, description="Project number is required - raffles are organized by project")
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    state: Optional[Literal["available", "sold", "reserved"]] = None
    set_number: Optional[int] = Field(None, ge=1)  # Cambié de set_id a set_number
    limit: int = Field(0, ge=0)
    offset: int = Field(0, ge=0)

class RaffleResponse(BaseModel):
    """Schema de respuesta para rifas"""
    user_id: int
    project_number: int
    raffle_number: int  # Cambié de number a raffle_number
    set_number: int
    buyer_user_id: Optional[int]
    buyer_number: Optional[int]
    payment_method: Optional[str]
    state: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
