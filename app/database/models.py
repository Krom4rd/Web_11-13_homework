from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    birthday: Mapped[Date] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(15), nullable=True)
    other_information: Mapped[str] = mapped_column(String, nullable=True)