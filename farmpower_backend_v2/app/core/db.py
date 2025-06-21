import logging
import sys
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if not SQLALCHEMY_DATABASE_URL:
    error_msg = "Error: DATABASE_URL environment variable is not set."
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Configure the database engine with connection pooling and timeouts
try:
    engine_args = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,    # Recycle connections after 5 minutes
        "pool_timeout": 30,     # Wait up to 30 seconds for a connection from the pool
        "max_overflow": 20,     # Allow up to 20 connections beyond pool_size
        "pool_size": 5,         # Maintain up to 5 persistent connections
    }

    # For SQLite, we need to add check_same_thread=False
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
        engine_args["connect_args"] = {"check_same_thread": False}
    
    # Log the database connection (but don't log credentials)
    db_log = SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL
    logger.info(f"Connecting to database: {db_log}")
    
    # Create the engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)
    
    # Test the connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database")
        
except Exception as e:
    error_msg = f"Failed to connect to the database: {str(e)}"
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get DB session.
    
    Yields:
        Session: A database session
        
    Raises:
        SQLAlchemyError: If there's an error creating or using the session
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
