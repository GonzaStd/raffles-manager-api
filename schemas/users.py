from pydantic import BaseModel, Field, EmailStr

class UserCredentials(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(...)