from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    
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


