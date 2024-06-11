import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()




class Settings(BaseSettings):

    secret_key: str = str(os.environ.get('SECRET_KEY'))
    algorithm: str = str(os.environ.get('ALGORITHM'))
    mail_username: str = str(os.environ.get('MAIL_USERNAME'))
    mail_password: str = str(os.environ.get('MAIL_PASSWORD'))
    mail_from: str = str(os.environ.get('MAIL_FROM'))
    mail_port: int = int(os.environ.get('MAIL_PORT'))
    mail_server: str = str(os.environ.get('MAIL_SERVER'))
    mail_from_name: str = str(os.environ.get('MAIL_FROM_NAME'))
    redis_host: str = str(os.environ.get('REDIS_HOST'))
    redis_port: int = int(os.environ.get('REDIS'))
    sqlalchemy_database_url: str = str(os.environ.get('SQLALCHEMY_DATABASE_URL'))

    # class Config:
    #     env_file = "../.env"
    #     env_file_encoding = "utf-8"
    


settings = Settings()


