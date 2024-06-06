from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from .models.models import User

class ContactBase(BaseModel):
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    birthday: date
    email: str = Field(max_length=128)
    phone_number: str = Field(max_length=15)
    other_information: Optional[str] = Field(default= None)
    
class ContactCreate(ContactBase):
    ...


class Contact(ContactBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    
    
class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True