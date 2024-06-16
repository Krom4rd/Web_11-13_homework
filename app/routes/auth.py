from typing import Annotated
from pathlib import Path

from fastapi import (APIRouter,
                    Depends,
                    HTTPException,
                    status,
                    Security,
                    BackgroundTasks,
                    Request,
                    Form,
                    UploadFile,
                    File,
                    Query)
from fastapi.security import (OAuth2PasswordRequestForm,
                              HTTPAuthorizationCredentials,
                              HTTPBearer)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from ..models import models
from ..database.database import get_db
from ..repository import auth_repo
from .. import schemas
from ..services import email as email_service
from ..services.auth import auth_service, Hash
from app.conf.config import settings_


hash_handler = Hash()
security = HTTPBearer()


router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=Path("app/services") / "templates")

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: schemas.UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user in database and send an email verification link.

    :param body: model UserCreate(username: str, email: EmailStr, password: str).
    :type body: schemas.UserCreate
    :param background_tasks: Background tasks for email sending.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access headers and other details.
    :type request: Request
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :return: {"user": new user model, "detail": ...}
    :rtype: json dict
    """    
    new_user = await auth_repo.create_user(body, db)
    if new_user:
        body.password = hash_handler.get_password_hash(body.password)
        background_tasks.add_task(email_service.send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user using email and password, returning JWT access and refresh tokens.

    :param body: The form data containing the email and password.
    :type body: OAuth2PasswordRequestForm, optional
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: Invalid email
    :raises HTTPException: Email not confirmed
    :raises HTTPException: Invalid password
    :return: {"access_token": str, "refresh_token": str, "token_type": "bearer"}
    :rtype: json dict
    """    
    user = await auth_repo.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refreshes authentication by validating an existing refresh token and
    issuing new tokens.

    :param credentials: Credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials, optional
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :raises HTTPException: Invalid refresh token
    :return: {"access_token": str, "refresh_token": str, "token_type": "bearer"}
    :rtype: json dict
    """    
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = db.query(models.User).filter(models.User.username == email).first()
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
async def root(current_user: Annotated[schemas.UserCreate, Depends(auth_service.get_current_user)]):
    """
    Retrieves the current user's profile information

    :param current_user: model UserCreate(username: str, email: EmailStr, password: str)
    :type current_user: Annotated[schemas.UserCreate, Depends
    :return: Database object.
    :rtype: models.User
    """    
    return current_user


@router.get("/secret")
async def read_item(current_user: models.User = Depends(auth_service.get_current_user)):
    """
    read_item _summary_

    _extended_summary_

    :param current_user: _description_, defaults to Depends(auth_service.get_current_user)
    :type current_user: models.User, optional
    :return: _description_
    :rtype: _type_
    """    
    return {"message": 'secret router', "owner": current_user.email}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms a user's email address using a token sent during registration.

    :param token: Token from email.
    :type token: str
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :raises HTTPException: Verification error
    :return: {"massage": ...}
    :rtype: json dict
    """    
    email = await auth_service.get_email_from_token(token)
    user = await auth_repo.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await auth_service.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post("/request_email")
async def request_email(body: schemas.RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)):
    """
    Sends a new email verification token if the initial token is lost
    or expired

    :param body: Email of the user requesting a new token.
    :type body: schemas.RequestEmail
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access host details for link generation.
    :type request: Request
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :return: {"massage": ...}
    :rtype: json dict
    """    
    user = await auth_repo.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(email_service.send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

@router.post("/password_recovery_message")
async def password_recovery_message(email: Annotated[str | None, Query(alias="email", example="test@test.test")],
                            background_tasks: BackgroundTasks,
                            request: Request,
                            db: Session = Depends(get_db)):
    """
    Sends a password reset link to the user's email if registeredin database.

    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access host details for link generation.
    :type request: Request
    :param email: Contains the email address for sending the reset link.
    :type email: EmailStr
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :raises HTTPException: Email not confirmed
    :raises HTTPException: Invalid email
    :return: {"message": ...}
    :rtype: json dict
    """    
    user = await auth_repo.get_user_by_email(email, db)
    if user and user.confirmed:
        metod = "recovery"
        background_tasks.add_task(email_service.send_email, user.email, user.username, request.base_url, metod)
        return {"message": "Check your email for recovery password."}
    elif user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email")

@router.get("/password_recovery/{token}")
async def password_reset_form(request: Request, token: str):
    """
    Rejects the password recovery form.

    :param request: Request object to access host details for link generation.
    :type request: Request
    :param token: Password recovery token.
    :type token: str
    :return: Password recovery form.
    :rtype: html form
    """    
    return templates.TemplateResponse(
        "password_rocovery_form.html", {"request": request, "token": token}
        )

@router.post("/password_recovery/{token}")
async def recovery_password_confirm(
    token: str, new_password: str = Form(...), db: Session = Depends(get_db)
    ):
    """
    Dependency validation function to set a new password
    for a user and save the new password to the database

    :param token: Password recovery token.
    :type token: str
    :param new_password: New password in a format familiar to the user.
    :type new_password: str, optional
    :param db: Generated database connection object, defaults to Depends(get_db).
    :type db: Session, optional
    :raises HTTPException: Invalid or expired token
    :raises HTTPException: User not found
    :return: {"message": ...}
    :rtype: json dict
    """    
    email = auth_service.get_email_from_recovery_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    user = await auth_repo.get_user_by_email(email, db)
    if user:
        await auth_repo.update_password(user,
                                        hash_handler.get_password_hash(new_password),
                                        db)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "Password changed successfully"}


@router.patch('/avatar', 
              response_model=schemas.User)
async def update_avatar_user(file: UploadFile = File(), current_user: models.User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)) -> models.User:
    """
    Update user avatar

    :param file: Image file.
    :type file: UploadFile, optional
    :param current_user: The user instance obtained after successful authentication.
    :type current_user: models.User, optional
    :param db: Generated database connection object, defaults to Depends(get_db)
    :type db: Session, optional
    :return: Database object.
    :rtype: models.User
    """    
    # Configuration       
    cloudinary.config( 
    cloud_name = settings_.cloud_name, 
    api_key = settings_.api_key, 
    api_secret = settings_.api_secret,
    secure=True
)
    r = cloudinary.uploader.upload(file.file, public_id=f'api/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'api/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await auth_repo.update_avatar(current_user, src_url, db)
    return user