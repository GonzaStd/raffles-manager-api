from pydantic import BaseModel, Field, model_validator
from typing import Optional

class BuyerCreate(BaseModel):
    name: str = Field(..., max_length=60)
    phone: str = Field(..., max_length=20)
    email: str = Field(max_length=100)

class BuyerDelete(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        id, name, phone = (self.id, self.name, self.phone)
        if id is None and (not name or not phone):
            raise ValueError("You must send 'id' or the 'name' and 'phone' pair.")
        return self

class BuyerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        name, phone, email = (self.name, self.phone, self.email)
        if name is None and phone is None and email is None:
            raise ValueError("You must modify/update at least one value.")
        return self