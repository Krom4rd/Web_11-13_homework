from typing import Annotated
from pathlib import Path

from fastapi import (APIRouter,
                    Depends,
                    HTTPException,
                    status,
                    Security,
                    BackgroundTasks,
                    Request,
                    Form)
from fastapi.security import (OAuth2PasswordRequestForm,
                              HTTPAuthorizationCredentials,
                              HTTPBearer)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..models import models
from ..database.database import get_db
from ..repository import auth_repo
from .. import schemas
from ..services import email as email_service
from ..services.auth import auth_service


hash_handler = auth_repo.Hash()
security = HTTPBearer()


router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=Path("app/services") / "templates")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: schemas.UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await auth_repo.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = hash_handler.get_password_hash(body.password)
    new_user = await auth_repo.create_user(body, db)
    background_tasks.add_task(email_service.send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await auth_repo.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_repo.create_access_token(data={"sub": user.username})
    refresh_token = await auth_repo.create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_repo.get_email_form_refresh_token(token)
    user = db.query(models.User).filter(models.User.username == email).first()
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_repo.create_access_token(data={"sub": email})
    refresh_token = await auth_repo.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
async def root(current_user: Annotated[schemas.UserCreate, Depends(auth_repo.get_current_user)]):
    return current_user


@router.get("/secret")
async def read_item(current_user: models.User = Depends(auth_repo.get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await auth_repo.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await auth_repo.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post("/request_email")
async def request_email(body: schemas.RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)):
    user = await auth_repo.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(email_service.send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

@router.post("/password_recovery_message")
async def password_recovery_message(body: schemas.RequestEmail,
                            background_tasks: BackgroundTasks,
                            request: Request,
                            db: Session = Depends(get_db)):
    user = await auth_repo.get_user_by_email(body.email, db)
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
    return templates.TemplateResponse(
        "password_rocovery_form.html", {"request": request, "token": token}
        )

@router.post("/password_recovery/{token}")
async def recovery_password_confirm(
    token: str, new_password: str = Form(...), db: Session = Depends(get_db)
):
    email = auth_service.verify_password_recovery_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    user = await auth_repo.get_user_by_email(email, db)
    if user:
        await auth_repo.update_password(user,
                                        auth_service.get_password_hash(new_password),
                                        db)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "Password changed successfully"}
