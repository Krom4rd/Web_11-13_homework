from sqlalchemy import Integer, String, Date, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)

    # def __repr__(self):
    #     print(self.username, type(self.username))
    #     return f"{self.username}"
    
    # contact_id= Column("contact_id", ForeignKey('contacts.id', ondelete='CASCADE'), default=None)
    # contacts = relationship("Contact", backref="users")


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
