from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models import models
from ..schemas import UserCreate
from ..conf.config import settings_

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_by_email(email: str, db: Session = Depends(get_db)) -> models.User | None:
    """
    Function for searching a user in the database by email.

    :param email: The user's email address needs to be found.
    :type email: str
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :return: Database object
    :rtype: models.User | None
    """    
    return db.query(models.User).filter(models.User.email == email).first()

async def create_user(body: UserCreate, db: Session= Depends(get_db)) -> models.User | None:
    """
    Function for writing to the user database.

    May cause an error if the new user's data matches an existing user: HTTP_409_CONFLICT.
    Email and username must be unique.
    
    :param body: model UserCreate(username: str, email: EmailStr, password: str).
    :type body: UserCreate
    :param db:  Generated database connection object
    :type db: Session
    :raises HTTPException: Account already exists error.
    :return: Add user to database and return models.User
    :rtype: models.User | None
    """    
    exist_user = db.query(models.User).filter_by(username=body.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this username already exists")
    else:
        exist_user = db.query(models.User).filter_by(email=body.email).first()
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email already exists")
    new_user = models.User(username=body.username, email=body.email, password=body.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_password(user: models.User, password: str, db: Session = Depends(get_db)) -> None:
    """
    Update_password the function of writing a new password for the user in database.

    WARNING! Password must be hashed.

    :param user: Object from the user database.
    :type user: models.User
    :param password: Hashed password.
    :type password: str
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    """    
    user.password = password
    db.commit()
    db.refresh(user)

async def update_avatar(user: models.User, url: str, db: Session = Depends(get_db)) -> models.User:
    """
    Function to store the path url to the new user avatar in the database.
    
    The path to the avatar must exist and be accessible.

    :param user: Object from the user database.
    :type user: models.User
    :param url: The path to the user's new avatar.
    :type url: str
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :return: Updated user model from database.
    :rtype: models.User
    """    
    user.avatar = url
    db.commit()
    return user
