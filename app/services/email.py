from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from ..services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME="education.test.python@gmail.com",
    MAIL_PASSWORD="vwef ykkg htdc dqvp",
    MAIL_FROM="education.test.python@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Oleh Novosad",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str, metod: str = "varification"):
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

