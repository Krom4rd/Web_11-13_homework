from sqlalchemy import Integer, String, Date, ForeignKey, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database import Base

default_avatar_url = (
    "https://res.cloudinary.com/restapp/image/upload/v1717342921/restapp/default.png"
)

class User(Base):
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
