from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import logging
import socket
from contextlib import contextmanager

from .config import settings

def resolve_ipv4(host):
    try:
        # Force IPv4 by explicitly requesting AF_INET
        addrinfo = socket.getaddrinfo(
            host,
            None,
            socket.AF_INET,  # Force IPv4
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )
        return addrinfo[0][4][0]  # Return the first IPv4 address
    except socket.gaierror as e:
        logging.warning(f"Could not resolve IPv4 for {host}: {e}")
        return None

def get_database_url():
    url = settings.DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set")
    
    # Parse host from URL
    try:
        host = url.split('@')[1].split(':')[0]
    except IndexError:
        logging.error(f"Invalid DATABASE_URL format: {url}")
        raise ValueError("Invalid DATABASE_URL format")
    
    # Force IPv4
    ipv4 = resolve_ipv4(host)
    if ipv4:
        logging.info(f"✅ Resolved IPv4 address for {host}: {ipv4}")
        return url.replace(host, ipv4)
    
    logging.warning(f"⚠️ Could not resolve IPv4 for {host}, using original hostname")
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