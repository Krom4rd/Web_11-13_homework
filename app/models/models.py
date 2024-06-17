from sqlalchemy import Integer, String, Date, ForeignKey, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database import Base

default_avatar_url = (
    "https://res.cloudinary.com/dyn9mlthg/image/upload/v1718192432/default.png"
)

class User(Base):
    """
    User database model

    The username and email class parameters are unique to the database.

    Pass the password only in hashed form

    Avatar url must be existing and readable

    :param id: primety_key
    :type id: int 
    :param username: str, unique=True
    :type username: str 
    :param email: EmailStr, unique=True
    :type email: str 
    :param password: password
    :type password: str
    :param refresh_token: encode refresh token
    :type refresh_token: str 
    :param avatar: url, default=True
    :type avatar: str 
    """    
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(
        String(255), nullable=True, default=default_avatar_url)


class Contact(Base):
    """
    Contact database model

    :param id: primary key
    :type id: int
    :param first_name: max length 32
    :type first_name: str
    :param last_name: max length 32
    :type last_name: str
    :param birthday: format(yyyy-mm-dd)
    :type birthday: date
    :param email: max length 128
    :type email: EmailStr
    :param phone_number: max length 15
    :type phone_number: str
    :param other_information: str
    :type other_information: str
    :param owner_id: ForeignKey('users.id')
    :type owner_id: int
    :param owner: relationship("User")
    :type owner: models.User
    """    
    
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    birthday: Mapped[Date] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(15), nullable=True)
    other_information: Mapped[str] = mapped_column(String, nullable=True)
    owner_id= Column(
        'user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None
    )
    owner = relationship("User", backref="contacts")
