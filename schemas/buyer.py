from datetime import datetime
from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import Optional

class BuyerCreate(BaseModel):
    """Schema for creating a new buyer"""
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')  # Phone required with regex
    email: Optional[EmailStr] = Field(None, max_length=100)  # Email optional but validated

class BuyerUpdate(BaseModel):
    """Schema for updating an existing buyer"""
    buyer_number: int = Field(..., ge=1)  # Changed from id to buyer_number
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')
    email: Optional[EmailStr] = Field(None, max_length=100)
    created_by_manager_number: Optional[int] = Field(None, ge=1)

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.name, self.phone, self.email]):
            raise ValueError("You must modify/update at least one value.")
        return self

class BuyerDeleteByNamePhone(BaseModel):
    """Schema for deleting buyer by name-phone"""
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')

class BuyerResponse(BaseModel):
    """Schema for buyer response"""
    entity_id: int
    buyer_number: int  # Changed from id to buyer_number
    name: str
    phone: str
    email: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_manager_number: Optional[int]

    class Config:
        from_attributes = True