from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional
from .models.models import User

class ContactBase(BaseModel):
    """
    Represents a contact entry in the database,
    storing personal and contact information.

    :param first_name: The contact's first name, a required field.
    :type first_name: String
    :param last_name: The contact's last name, a required field.
    :type last_name: String
    :param birthday: The contact's date of birth, an optional field.
    :type birthday: Date
    :param email: The contact's email address, must be unique.
    :type email: String
    :param phone_number: The contact's phone number, an optional field.
    :type phone_number: String
    :param other_information: Other information or notes about the contact,\
                            stored as text and is optional.
    :type other_information: String
    """
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
    email: EmailStr



class UserCreate(UserBase):
    password: str
    
    
class User(UserBase):
    id: int
    contacts: list[Contact] = []
    avatar: str
    
    class Config:
        from_attributes = True


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

