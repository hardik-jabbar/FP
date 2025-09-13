from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import logging

from .config import settings

def get_database_url():
    # Remove any hostaddr parameter if present
    url = settings.DATABASE_URL
    if "hostaddr=" in url:
        url = url.split("?")[0]
    return url

def create_db_engine():
    retries = 5
    retry_delay = 1

    for attempt in range(retries):
        try:
            engine = create_engine(
                get_database_url(),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={
                    "connect_timeout": 10,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5
                }
            )
            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except OperationalError as e:
            if attempt == retries - 1:
                raise
            logging.warning(f"Database connection attempt {attempt + 1}/{retries} failed: {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)