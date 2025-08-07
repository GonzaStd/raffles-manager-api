from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional


class RaffleSetCreate(BaseModel):
    project_id: int
    name: str = Field(..., max_length=60)
    type: Literal["online", "physical"]
    requested_count: int = Field(..., gt=0) # Not in database, used for raffles creation
    unit_price: int = Field(..., gt=0)

class RaffleSetOut(BaseModel):
    id: int
    name: str
    init: int
    final: int
    unit_price: int

    class Config:
        from_attributes = True

class RaffleSetUpdate(BaseModel):
    id: int
    name: Optional[str] = Field(..., max_length=60)
    type: Optional[Literal["online", "physical"]] = Field(...)
    unit_price: Optional[int] = Field(..., gt=0)

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def check_valid_fields(self):
        id, name, type, unit_price = (self.id, self.name, self.type, self.unit_price)
        if id:
            if name or not type or not unit_price:
                raise ValueError("You must modify/update at least one value.")
        else:
            raise ValueError("Set id is required.")
        return self