from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional

class RaffleUpdate(BaseModel):
    number: int
    buyer_id: Optional[int] = None
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    state: Optional[Literal["available", "sold", "reserved"]] = None

    @model_validator(mode="after")
    def check_valid_fields(self):
        number, buyer_id, payment_method, state = (self.number, self.buyer_id, self.payment_method, self.state)
        if number:
            if buyer_id is None and payment_method is None and state is None:
                raise ValueError("You must modify/update at least one value.")
        else:
            raise ValueError("Raffle number is required.")
        return self

class RafflePayment(BaseModel):
    number: int
    buyer_id: int
    payment_method: Literal["cash", "card", "transfer"]
    state: Literal["sold", "reserved"]

    @model_validator(mode="after")
    def check_valid_fields(self):
        if not self.number or not self.buyer_id or not self.payment_method or not self.state:
            raise ValueError("All fields are required for payment.")
        return self