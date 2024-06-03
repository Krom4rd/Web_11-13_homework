from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ResponseContact(BaseModel):
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    birthday: date
    email: str = Field(max_length=128)
    phone_number: str = Field(max_length=15)
    other_information: Optional[str] = Field(default= None)
    
    class Config:
        orm_mode = True