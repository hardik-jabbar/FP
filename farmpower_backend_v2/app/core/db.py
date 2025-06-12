from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings # Import settings from config.py

# Use DATABASE_URL from settings, with a fallback if it's None (though it should be set in .env)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL or "postgresql://fallback_user:fallback_password@localhost/fallback_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
