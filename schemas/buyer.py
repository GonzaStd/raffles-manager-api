from datetime import datetime
from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import Optional

class BuyerCreate(BaseModel):
    """Schema para crear un nuevo comprador"""
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')  # Phone obligatorio con regex
    email: Optional[EmailStr] = Field(None, max_length=100)  # Email opcional pero validado

class BuyerUpdate(BaseModel):
    """Schema para actualizar un comprador existente"""
    buyer_number: int = Field(..., ge=1)  # Cambié de id a buyer_number
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')
    email: Optional[EmailStr] = Field(None, max_length=100)

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not any([self.name, self.phone, self.email]):
            raise ValueError("You must modify/update at least one value.")
        return self

class BuyerDeleteByNamePhone(BaseModel):
    """Schema para eliminar comprador por nombre-teléfono"""
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20, pattern=r'^\+?\d[\d\s\-\(\)]{8,18}$')

class BuyerResponse(BaseModel):
    """Schema de respuesta para compradores"""
    user_id: int
    buyer_number: int  # Cambié de id a buyer_number
    name: str
    phone: str
    email: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True