from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import Optional

class BuyerCreate(BaseModel):
    name: str = Field(..., max_length=60)
    phone: str = Field(..., max_length=20, pattern=r'^\+?\s?\d[\d\s]{5,17}$')
    email: Optional[EmailStr] = Field(max_length=100)

class BuyerDelete(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = Field(max_length=20, pattern=r'^\+?\s?\d[\d\s]{5,17}$')

    @model_validator(mode="after")
    def check_valid_fields(self):
        id, name, phone = (self.id, self.name, self.phone)
        if id is None and (not name or not phone):
            raise ValueError("You must send 'id' or the 'name' and 'phone' pair.")
        return self

class BuyerUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    phone: Optional[str] = Field(max_length=20, pattern=r'^\+?\s?\d[\d\s]{5,17}$')
    email: Optional[EmailStr] = Field(max_length=100)

    @model_validator(mode="after")
    def check_valid_fields(self):
        id, name, phone, email = (self.id, self.name, self.phone, self.email)
        if id:
            if name is None and phone is None and email is None:
                raise ValueError("You must modify/update at least one value.")
        else:
            raise ValueError("Buyer id is required.")
        return self