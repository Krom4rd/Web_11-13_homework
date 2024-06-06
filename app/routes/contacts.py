from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.orm import Session 

from ..database.database import get_db
from ..models.models import Contact, User
from ..schemas import ContactBase
from ..repository import auth_repo, contacts_repo
from ..services.auth import auth_service
from .. import schemas


router = APIRouter(prefix="/contact", tags=["contacts"])

@router.get("/{contact_id}", response_model=schemas.Contact)
async def get_contact_by_id(
    contact_id: Annotated[int, Path(title="The id of contact to get")],
    db: Session = Depends(get_db),
    user = Depends(auth_repo.get_current_user)
    ):
    result = await contacts_repo.get_contact_with_id(contact_id=contact_id,
                                                     db=db,
                                                     user=user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return result

@router.get("/", response_model=list[schemas.Contact])
async def all_contacts(db: Session = Depends(get_db),
                       user = Depends(auth_repo.get_current_user))-> list[schemas.Contact]:
    result = await contacts_repo.get_all_contact(db, user)
    return result


@router.post("/", response_model=schemas.Contact)
async def add_new_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)):

    contact = await contacts_repo.create_contact(db, contact, user)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: Annotated[int, Path(title="The id of contact to get")],
    user = Depends(auth_repo.get_current_user),
    db: Session = Depends(get_db)
    ):
    result =  await contacts_repo.delete_contact(contact_id=contact_id,
                                              user=user,
                                              db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cotact not found"
        )
    return result

@router.get("/search_by/", response_model=list[schemas.Contact])
async def search_by_filter(
        user: User = Depends(auth_repo.get_current_user),
        first_name: Annotated[str | None, Query(alias="first name", example="string")] = None,
        last_name: Annotated[str | None, Query(alias="last name", example="string")] = None,
        email: Annotated[str | None, Query(alias="email", example="test@test.test")] = None,
        db: Session=Depends(get_db)) -> list[Contact] | None:
    result =  await contacts_repo.get_contacts_with_filter(user=user,
                                                        db=db,
                                                        first_name_=first_name,
                                                        last_name_=last_name,
                                                        email_=email)
    if result == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return result


@router.get("/birthdays/", response_model=list[schemas.Contact])
async def get_upcoming_birthdays(db: Session = Depends(get_db),
                                 user = Depends(auth_repo.get_current_user)):                               
    result = await contacts_repo.get_upcoming_birthdays(user=user,
                                                         db=db)
    return result


@router.patch("/{contact_id}", response_model=ContactBase)
async def update_contact(contact_id: int,
                         update_body: ContactBase,
                         db: Session = Depends(get_db),
                         user = Depends(auth_repo.get_current_user)):
    result = await contacts_repo.update_contact(contact_id=contact_id,
                                                update_body=update_body,
                                                db=db,
                                                user=user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return result

