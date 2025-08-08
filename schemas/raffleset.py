from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Literal, Optional


class RaffleSetCreate(BaseModel):
    project_id: int
    name: str = Field(..., max_length=60)
    type: Literal["online", "physical"]
    requested_count: int = Field(..., gt=0) # Not in database, used for raffles creation
    unit_price: int = Field(..., gt=0)

class RaffleSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    init: int
    final: int
    unit_price: int

class RaffleSetUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = Field(None, max_length=60)
    type: Optional[Literal["online", "physical"]] = Field(None)
    unit_price: Optional[int] = Field(None, gt=0)

    @model_validator(mode="after")
    def check_valid_fields(self):
        id, name, type, unit_price = (self.id, self.name, self.type, self.unit_price)
        if id:
            if name is None and type is None and unit_price is None:
                raise ValueError("You must modify/update at least one value.")
        else:
            raise ValueError("Set id is required.")
        return self