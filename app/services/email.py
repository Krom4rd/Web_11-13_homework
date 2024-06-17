from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from ..services.auth import auth_service
from ..conf.config import settings_

# Email configuration using settings from the application configuration
conf = ConnectionConfig(
    MAIL_USERNAME=str(settings_.mail_username),
    MAIL_PASSWORD=str(settings_.mail_password),
    MAIL_FROM=str(settings_.mail_from),
    MAIL_PORT=int(settings_.mail_port),
    MAIL_SERVER=str(settings_.mail_server),
    MAIL_FROM_NAME=str(settings_.mail_from_name),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str, metod: str = "varification") -> None:
    """
    Function for sending emails.

    There are 2 variants of varification and recovery.

    :param email: Email as a string.
    :type email: EmailStr
    :param username: The username of the recipient, used for personalising the email.
    :type username: str
    :param host: The base URL of the host, used to create the link for email verification or recovery passsword.
    :type host: str
    :param metod: "varification" or "recovery", defaults to "varification".
    :type metod: str, optional
    """    
    try:
        if metod == "varification":
            subject = "Confirm your email "
            template_name = "email_template.html"
            token = auth_service.create_email_token({"sub": email})
        elif metod == "recovery":
            subject = "Password recovery"
            template_name = "password_recovery.html"
            token = auth_service.create_password_recovery_token(email)
        
        message = MessageSchema(
            subject= subject,
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=template_name)
    except ConnectionErrors as err:
        print(err)

