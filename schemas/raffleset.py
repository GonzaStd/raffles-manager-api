from pydantic import BaseModel, Field
from typing import Literal

class RaffleSetCreate(BaseModel):
    project_id: int
    name: str = Field(..., max_length=60)
    type: Literal["online", "physical"]
    requested_count: int = Field(..., gt=0)
    unit_price: int = Field(..., gt=0)

class RaffleSetOut(BaseModel):
    id: int
    name: str
    init: int
    final: int
    unit_price: int

    class Config:
        orm_mode = True
