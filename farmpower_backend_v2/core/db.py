from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import logging
import socket
from contextlib import contextmanager

from .config import settings

def is_ipv4_available(host):
    try:
        socket.getaddrinfo(host, None, socket.AF_INET)
        return True
    except socket.gaierror:
        return False

def get_database_url():
    url = settings.DATABASE_URL
    
    # Parse host from URL
    host = url.split('@')[1].split(':')[0]
    
    # Force IPv4 if available
    if is_ipv4_available(host):
        ipv4 = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
        return url.replace(host, ipv4)
    
    return url

def create_db_engine():
    retries = 5
    retry_delay = 1
    last_error = None

    for attempt in range(retries):
        try:
            engine = create_engine(
                get_database_url(),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={
                    "connect_timeout": 30,
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5,
                    "options": "-c statement_timeout=60000"  # 60 second timeout
                }
            )

            # Add event listeners for connection debugging
            @event.listens_for(engine, 'connect')
            def receive_connect(dbapi_connection, connection_record):
                logging.info("New database connection established")

            @event.listens_for(engine, 'checkout')
            def receive_checkout(dbapi_connection, connection_record, connection_proxy):
                logging.info("Database connection checked out from pool")

            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                logging.info("✅ Database connection test successful")
            return engine

        except OperationalError as e:
            last_error = e
            if attempt == retries - 1:
                logging.error(f"Failed to connect to database after {retries} attempts")
                logging.error(f"Last error: {str(last_error)}")
                raise
            logging.warning(f"Database connection attempt {attempt + 1}/{retries} failed: {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Context manager for database sessions
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()