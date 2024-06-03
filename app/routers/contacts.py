from typing import Annotated
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import extract, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..database.database import get_db
from ..database.models import Contact
from ..schemas import ResponseContact


router = APIRouter(prefix="/contact", tags=["contacts"])


@router.get("/", response_model=list[ResponseContact])
async def all_contacts(db: Session=Depends(get_db)):
    result = db.query(Contact).all()
    return result


@router.get("/search_by/", response_model=list[ResponseContact])
async def one_or_more_search_filters(
        id_: Annotated[int | None, Query(alias="id", example="integer")] = None,
        first_name_: Annotated[str | None, Query(alias="first_name", example="string")] = None,
        last_name_: Annotated[str | None, Query(alias="last_name", example="string")] = None,
        email_: Annotated[str | None, Query(alias="email", example="test@test.test")] = None,
        db: Session=Depends(get_db)) -> list[Contact]:
    result = []
    if id_:
        try:
            result.append(db.get_one(Contact, id_))
        except NoResultFound:
            pass
    if first_name_:
        result.extend([contact for contact in db.query(Contact).filter_by(first_name = first_name_).all()])
    if last_name_:
        result.extend([contact for contact in db.query(Contact).filter_by(last_name = last_name_).all()])
    if email_:
        result.extend([contact for contact in db.query(Contact).filter_by(email = email_).all()])
    return result


@router.get("/birthdays", response_model=list[ResponseContact])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    in_a_week = today + timedelta(days=7)
    if today.month == in_a_week.month:
        return db.query(Contact).filter(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day,
                extract('day', Contact.birthday) <= in_a_week.day
            )
        ).all()
    else:
        return db.query(Contact).filter(
            or_(
                and_(
                    extract('month', Contact.birthday) == today.month,
                    extract('day', Contact.birthday) >= today.day
                ),
                and_(
                    extract('month', Contact.birthday) == in_a_week.month,
                    extract('day', Contact.birthday) <= in_a_week.day
                )
            )
        ).all()


@router.post("/")
async def post_contact(contact: ResponseContact,
                       db: Session=Depends(get_db)):
    contact = contact.model_dump() 
    other_information = None
    if contact.get('other_information'):
        other_information = contact.get('other_information')
    contact = Contact(id = None,
                      first_name= contact['first_name'],
                      last_name= contact['last_name'],
                      birthday= contact['birthday'],
                      email= contact['email'],
                      phone_number= contact['phone_number'],
                      other_information = other_information
                      )
    try:
        db.add(contact)
        db.commit()
        db.refresh(contact)
    except IntegrityError as err:
        raise HTTPException(status_code=409, detail=err.__repr__())
    return contact


@router.patch("/{contact_id}", response_model=ResponseContact)
async def update_contact(contact_id: int,
                         update_body: ResponseContact,
                         db: Session = Depends(get_db)):
    contact = db.get_one(Contact, contact_id)
    if contact:
        update_data = update_body.model_dump()
        for key, value in update_data.items():
            if key == "birthday" and value == date.today():
                continue
            if value == "string":
                continue
            setattr(contact, key, value)
    try:
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=409, detail=err.__repr__())
    return contact


@router.delete("/{contact.id}", response_model=ResponseContact)
async def delete_contact(contact_id: int,
                         db: Session = Depends(get_db)):
    contact = db.get_one(Contact, contact_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact