from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings - class to configure dependencies
    gets the data from the .env file and assigns it to variables in this class

    :param secret_key: Secret key used for cryptographic operations.
    :type secret_key: String
    :param algorithm: Algorithm used for JWT encoding and decoding.
    :type algorithm: String
    :param mail_username: Username for the mail service.
    :type mail_username: String
    :param mail_password: Password for the mail service.
    :type mail_password: String
    :param mail_from: Sender email address.
    :type mail_from: EmailString
    :param mail_port: Port number for the mail server.
    :type mail_port: Integer
    :param mail_server: Hostname of the mail server.
    :type mail_server: String
    :param redis_host: Hostname for Redis server, defaults to 'localhost'.
    :type redis_host: String
    :param redis_port: Port number for the Redis server, defaults to 6379.
    :type redis_port: Integer
    :param cloudinary_name: Cloudinary cloud name for media storage.
    :type cloudinary_name: String
    :param cloudinary_api_key: API key for Cloudinary.
    :type cloudinary_api_key: String
    :param cloudinary_api_secret: API secret for Cloudinary.
    :type cloudinary_api_secret: String
    """ 
    secret_key: str 
    algorithm: str
    mail_username: str
    mail_password: str 
    mail_from: str 
    mail_port: int
    mail_server: str 
    mail_from_name: str 
    redis_host: str 
    redis_port: int
    sqlalchemy_database_url: str
    cloud_name: str
    api_key: str
    api_secret: str

    model_config = SettingsConfigDict(env_file = ".env", extra="ignore")
    


settings_ = Settings()


