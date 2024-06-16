from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.conf.config import settings_

SQLALCHEMY_DATABASE_URL = settings_.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    
    """
    Database connection generator.

    :yield: Session
    :rtype: Session
    """    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()