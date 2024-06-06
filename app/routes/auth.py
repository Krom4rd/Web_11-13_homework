from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..models import models

from ..database.database import get_db
from ..repository import auth_repo
from .. import schemas


hash_handler = auth_repo.Hash()
security = HTTPBearer()


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserBase)
async def signup(body: schemas.UserCreate, db: Session = Depends(get_db)):
    exist_user = db.query(models.User).filter_by(username=body.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    new_user = models.User(username=body.username, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=body.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")   
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_repo.create_access_token(data={"sub": user.username})
    refresh_token = await auth_repo.create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}  #"refresh_token": refresh_token, 


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