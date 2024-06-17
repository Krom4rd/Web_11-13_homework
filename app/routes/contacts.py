from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.orm import Session 
from fastapi_limiter.depends import RateLimiter

from ..database.database import get_db
from ..models import models
from ..schemas import ContactBase
from ..repository import contacts_repo
from ..services.auth import auth_service
from .. import schemas


router = APIRouter(prefix="/contact", tags=["contacts"])

@router.get("/{contact_id}",
            response_model=schemas.Contact,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_id(
    contact_id: Annotated[int, Path(title="The id of contact to get")],
    db: Session = Depends(get_db),
    user: models.User = Depends(auth_service.get_current_user)
    ) -> models.Contact | None:
    """
    Get contact from database by id.

    :param contact_id: The id of contact to get.
    :type contact_id: Annotated[int, Path, optional
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :param user: User object from database.
    :type user: _type_, optional
    :raises HTTPException: Contact not found
    :return: Object class Contact if found.
    :rtype: models.Contact | None
    """    
    result = await contacts_repo.get_contact_with_id(contact_id=contact_id,
                                                     db=db,
                                                     user=user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result

@router.get("/",
            response_model=list[schemas.Contact],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def all_contacts(db: Session = Depends(get_db),
                       user: models.User = Depends(auth_service.get_current_user))-> list[models.Contact]:
    """
    Get all user contacts.

    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :param user: User object from database.
    :type user: models.User, optional
    :return: All user contacts
    :rtype: list[models.Contact]
    """    
    
    result = await contacts_repo.get_all_contact(db, user)
    return result


@router.post("/",
             response_model=schemas.Contact,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def add_new_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth_service.get_current_user)) -> models.Contact:
    """
    Creating and recording a new contact in the database.

    :param contact: model ContactCreate(\n
    first_name: str \n
    last_name: str \n
    birthday: date\n
    email: str \n
    phone_number: str \n
    other_information: Optional[str] \n
    ).
    :type contact: schemas.ContactCreate
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :param user: User object from database.
    :type user: models.User, optional
    :return: Database object
    :rtype: models.Contact
    """    
    contact = await contacts_repo.create_contact(db, contact, user)
    return contact

@router.delete("/{contact_id}",
               dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(
    contact_id: Annotated[int, Path(title="The id of contact to get")],
    user: models.User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
    ) -> None:
    """
    Delete the contact from the database.

    :param contact_id: The id of contact to delete.
    :type contact_id: Annotated[int, Path, optional
    :param user: User object from database.
    :type user: models.User, optional
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :raises HTTPException: Cotact not found
    :return: None
    :rtype: None
    """    
    result =  await contacts_repo.delete_contact(contact_id=contact_id,
                                              user=user,
                                              db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cotact not found"
        )
    return result

@router.get("/search_by/",
            response_model=list[schemas.Contact],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_by_filter(
        user: models.User = Depends(auth_service.get_current_user),
        first_name: Annotated[str | None, Query(alias="first name", example="string")] = None,
        last_name: Annotated[str | None, Query(alias="last name", example="string")] = None,
        email: Annotated[str | None, Query(alias="email", example="test@test.test")] = None,
        db: Session=Depends(get_db)) -> list[models.Contact] | None:
    """
    Search for a contact in the database by filters.


    :param user: User object from database.
    :type user: models.User, optional
    :param first_name: Search query by first name.
    :type first_name: str
    :param last_name: Search query by last name.
    :type last_name: str
    :param email: Search query by email.
    :type email: str
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: Contact not found.
    :return: Search result among contacts.
    :rtype: list[models.Contact] | None
    """    
    result =  await contacts_repo.get_contacts_with_filter(user=user,
                                                        db=db,
                                                        first_name_=first_name,
                                                        last_name_=last_name,
                                                        email_=email)
    if result == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


@router.get("/birthdays/",
            response_model=list[schemas.Contact],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_upcoming_birthdays(db: Session = Depends(get_db),
                                 user: models.User = Depends(auth_service.get_current_user)) -> list[models.Contact]:
    """
    Get contacts whose birthday will be in the next 7 days.

    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :param user: User object from database.
    :type user: models.User, optional
    :return: Objects class Contact if found.
    :rtype: list[models.Contact]
    """    
    result = await contacts_repo.get_upcoming_birthdays(user=user,
                                                         db=db)
    return result


@router.patch("/{contact_id}",
              response_model=ContactBase,
              dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(contact_id: int,
                         update_body: ContactBase,
                         db: Session = Depends(get_db),
                         user: models.User = Depends(auth_service.get_current_user)) -> models.Contact | None:
    """
    Update contact information

    :param contact_id: The id of contact to update.
    :type contact_id: int
    :param update_body: model ContactBase(\n
    first_name: str \n
    last_name: str \n
    birthday: date\n
    email: str \n
    phone_number: str \n
    other_information: Optional[str] \n
    ).
    :type update_body: ContactBase
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :param user: User object from database.
    :type user: models.User, optional
    :raises HTTPException: Contact not found.
    :return: New contact model.
    :rtype: models.Contact | None
    """    
    result = await contacts_repo.update_contact(contact_id=contact_id,
                                                update_body=update_body,
                                                db=db,
                                                user=user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result

