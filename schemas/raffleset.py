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
        orm_mode = True

class RaffleSetUpdate(BaseModel):
    name: Optional[str] = Field(..., max_length=60)
    type: Optional[str] = Literal["online", "physical"]
    unit_price: Optional[int] = Field(..., gt=0)

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not self.name or not self.type or not self.unit_price:
            raise ValueError("You must modify/update at least one value.")
        return self