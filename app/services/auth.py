from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import redis 

from ..database.database import get_db
from ..models import models
from ..repository import auth_repo
from ..conf.config import settings_


class Hash:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password, hashed_password) -> bool:
        
        """
        Verifies a given string password against the hashed password.

        :param plain_password: Password in a format familiar to the user.
        :type plain_password: str
        :param hashed_password: The hash of the password to compare against.
        :type hashed_password: bool
        :return: True if the password is correct, False otherwise.
        :rtype: bool
        """        
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generates a password hash from a string password.

        The hashed password is required to write to the database.

        :param password: Password in a format familiar to the user.
        :type password: str
        :return: hashed password
        :rtype: str
        """        
        return self.pwd_context.hash(password)
class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = str(settings_.secret_key)
    ALGORITHM = str(settings_.algorithm)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    r = redis.Redis(host=settings_.redis_host, port=settings_.redis_port, db=0)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates a JWT access token with an optional expiry delta.

        :param data: The data to encode in the token, typically containing the user's identity.
        :type data: dict
        :param expires_delta: The number of seconds until the token expires, defaults to None.
        :type expires_delta: Optional[float], optional
        :return: Encoded jwt access token.
        :rtype: str
        """        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates a JWT refresh token used to obtain new access tokens.

        :param data: The data to encode in the token.
        :type data: dict
        :param expires_delta: The number of seconds until the token expires., defaults to None.
        :type expires_delta: Optional[float], optional
        :return: Encoded jwt refresh token.
        :rtype: str
        """        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Function to get the user's email from refresh token.

        :param refresh_token: Token.
        :type refresh_token: str
        :raises HTTPException: Invalid scope for token.
        :raises HTTPException: Could not validate credentials.
        :return: Email.
        :rtype: str
        """    
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
        """
        Retrieves the current user from a JWT token.

        :param token: The JWT token to decode, defaults to Depends(oauth2_scheme).
        :type token: str, optional
        :param db: Generated database connection object, defaults to Depends(get_db).
        :type db: Session, optional
        :raises credentials_exception: Could not validate credentials.
        :return: Database object.
        :rtype: models.User
        """        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = auth_repo.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def confirmed_email(email: str, db: Session) -> None:
        """
        The confirmed_email function is used to confirm a user's email address.

        :param email: Email address of the user.
        :type email: str
        :param db: Generated database connection object, defaults to Depends(get_db).
        :type db: Session, optional
        """ 
        user = auth_repo.get_user_by_email(email, db)
        user.confirmed = True
        db.commit()

    async def get_email_from_email_token(self, token: str) -> str:
        """
        Function to get the user's email from email token.

        :param token: Token for email verification.
        :type token: str
        :raises HTTPException: Invalid token for email verification.
        :return: Email.
        :rtype: str
        """           
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


    def create_email_token(self, data: dict) -> str:
        """
        Create token for user email verification .

        :param data: The data to include in the token, the user's email.
        :type data: dict
        :return: The encoded token.
        :rtype: str
        """        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    def create_password_recovery_token(self, email: str) -> str:
        """
        Create password recovery token from email.

        :param email: Email in database user.
        :type email: str
        :return: The encoded token.
        :rtype: str
        """        
        expire = datetime.utcnow() + timedelta(minutes=15)
        payload = {"exp": expire, "email": email}
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_email_from_recovery_token(self, token: str) -> str:
        """
        Function to get the user's email from recovery token.

        :param token: Token to decode.
        :type token: str
        :raises HTTPException: Could not validate credentials
        :return: Email.
        :rtype: str
        """        
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload["email"]
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        


auth_service = Auth()
