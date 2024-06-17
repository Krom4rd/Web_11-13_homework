from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


from .. import schemas
from ..models import models


async def get_all_contact(db: Session, user: models.User) -> list[models.Contact]:
    """
    Function to retrieve all user contacts.

    :param db: Generated database connection object
    :type db: Session
    :param user: User object to find their contacts.
    :type user: models.User
    :return: List of all contacts.
    :rtype: list[models.Contact]
    """    
    contacts = db.query(models.Contact).filter(and_(models.Contact.owner_id == user.id)).all()
    return contacts


async def create_contact(db: Session, contact: schemas.Contact, user: models.User) -> models.Contact:
    """
    Function to create a new contact for the user.

    Checks the validity of the entered data to create a new contact,
    if successful, adds the new contact to the user's contacts.

    :param db: Generated database connection object
    :type db: Session
    :param contact: Validation of the contact class object.
    :type contact: schemas.Contact
    :param user: User object to add a new contact.
    :type user: schemas.User
    :return: The contact class object just written.
    :rtype: models.Contact
    """    
    db_contact = models.Contact(first_name=contact.first_name,
                                last_name=contact.last_name,
                                birthday=contact.birthday,
                                email=contact.email,
                                phone_number=contact.phone_number,
                                other_information=contact.other_information,
                                owner_id=user.id
                                )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

async def get_contact_with_id(contact_id: int,
                              db: Session,
                              user: models.User) -> models.Contact | None:  
    """
    A function that searches for a contact by id.

    Search for a contact by its ID. If the contact was found,
    it will return an object of the models.Contact.
    In case of failure, None will be returned.

    :param contact_id: Contact id.
    :type contact_id: int
    :param db: Generated database connection object.
    :type db: Session
    :param user: User object to find contacts.
    :type user: models.User
    :return: Contact or None.
    :rtype: models.Contact | None
    """    
    return db.query(models.Contact).filter(and_(models.Contact.id == contact_id,
                                                  models.Contact.owner_id == user.id)).first()

async def get_contacts_with_filter(user: models.User,
        db: Session,
        first_name_: str = None,
        last_name_: str = None,
        email_: str = None) -> list[models.Contact] | None:
    """
    A function for searching the user's contacts according to the specified parameters.

    Any of the search parameters is optional.
    You can use one or several search parameters at the same time.

    :param user: User object to find contacts.
    :type user: models.User
    :param db: Generated database connection object.
    :type db: Session
    :param first_name_: Contact search by first name, defaults to None.
    :type first_name_: str, optional
    :param last_name_: Contact search by last name, defaults to None.
    :type last_name_: str, optional
    :param email_: Contact search by email, defaults to None.
    :type email_: str, optional
    :return: A list of models.Contact objects.
    :rtype: list[models.Contact] | None
    """    
    result = []
    user_contacts = db.query(models.Contact).filter_by(owner_id = user.id).all()
    for contact in user_contacts:
        if first_name_:
            if contact.first_name == first_name_:
                result.append(contact)
                continue
        if last_name_:
            if contact.last_name == last_name_:
                result.append(contact)
                continue
        if email_:
            if contact.email == email_:
                result.append(contact)
                continue

    return result

async def delete_contact(contact_id: int,
                         user: models.User,
                         db: Session) -> models.Contact | None:
    """
    A function for deleting a contact from a user.

    Can delete a user's contact after receiving the contact id.

    :param contact_id: Contact id.
    :type contact_id: int
    :param db: Generated database connection object.
    :type db: Session
    :param user: User object to find contacts.
    :type user: models.User
    :return: Contact or None.
    :rtype: models.Contact | None
    """    
    user_contacts = db.query(models.Contact).filter(and_(models.Contact.id == contact_id,
                                                         models.Contact.owner_id == user.id)).first()
    if user_contacts:
        db.delete(user_contacts)
        db.commit()
    return user_contacts

async def get_upcoming_birthdays(user: models.User, db: Session) -> list[models.Contact] | None:
    """
    A function for finding contacts whose birthday will be in the next 7 days.

    If there are none, it will return None.
    
    :param user: User object to find contacts.
    :type user: models.User
    :param db: Generated database connection object.
    :type db: Session
    :return: A list of models.Contact objects.
    :rtype: list[models.Contact] | None
    """    
    today = date.today()
    in_a_week = today + timedelta(days=7)
    if today.month == in_a_week.month:
        return db.query(models.Contact).filter(
            and_(
                models.Contact.owner_id == user.id,
                extract('month', models.Contact.birthday) == today.month,
                extract('day', models.Contact.birthday) >= today.day,
                extract('day', models.Contact.birthday) <= in_a_week.day
            )
        ).all()
    else:
        return db.query(models.Contact).filter(
            and_(
                models.Contact.owner_id == user.id,
                or_(
                    and_(
                        extract('month', models.Contact.birthday) == today.month,
                        extract('day', models.Contact.birthday) >= today.day
                    ),
                    and_(
                        extract('month', models.Contact.birthday) == in_a_week.month,
                        extract('day', models.Contact.birthday) <= in_a_week.day
                    )
                )
            )
        ).all()
    
async def update_contact(contact_id: int,
                         update_body: schemas.ContactBase,
                         db:Session,
                         user: models.User) -> models.Contact | None:
    """
    A function for updating data in a contact.

    To make changes to a contact,
    it is necessary to specify the ID of the contact that needs to be updated,
    to transfer the data for updating in the appropriate format.
    
    :param contact_id: Contact id.
    :type contact_id: int
    :param update_body: Validation of the contact class object.
    :type update_body: schemas.ContactBase
    :param db: Generated database connection object.
    :type db: Session
    :param user: User object to add a new contact.
    :type user: models.User
    :raises HTTPException: possible conflict of data validity.
    :return: The contact models.Contact just written or None.
    :rtype: models.Contact | None
    """    
    user_contact = db.query(models.Contact).filter(and_(models.Contact.id == contact_id,
                                                        models.Contact.owner_id == user.id)).first()
    if user_contact:
        update_data = update_body.model_dump()
        for key, value in update_data.items():
            if key == "birthday" and value == date.today():
                continue
            if value == "string":
                continue
            setattr(user_contact, key, value)
    try:
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.__repr__())
    return user_contact
