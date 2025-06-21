import logging
import sys
import time
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get the database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if not SQLALCHEMY_DATABASE_URL:
    error_msg = "Error: DATABASE_URL environment variable is not set."
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

def create_db_engine(max_retries: int = 3, retry_delay: int = 2):
    """Create a database engine with retry logic."""
    attempts = 0
    last_exception = None
    
    engine_args = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,    # Recycle connections after 5 minutes
        "pool_timeout": 30,     # Wait up to 30 seconds for a connection from the pool
        "max_overflow": 20,     # Allow up to 20 connections beyond pool_size
        "pool_size": 5,         # Maintain up to 5 persistent connections
        "echo": True,          # Log SQL queries (useful for debugging)
    }

    
    # For SQLite, we need to add check_same_thread=False
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        # For PostgreSQL, set a statement timeout
        engine_args["connect_args"] = {"connect_timeout": 10, "options": "-c statement_timeout=30000"}
    
    # Log the database connection (but don't log credentials)
    db_log = SQLALCHEMY_DATABASE_URL.split('@')[-1] if '@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL
    
    while attempts < max_retries:
        try:
            logger.info(f"Attempt {attempts + 1}/{max_retries} - Connecting to database: {db_log}")
            
            # Create the engine
            engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)
            
            # Test the connection with a simple query
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Successfully connected to the database")
                return engine
                
        except OperationalError as e:
            last_exception = e
            logger.warning(f"Database connection attempt {attempts + 1} failed: {str(e)}")
            if attempts < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(retry_delay * (attempts + 1))  # Exponential backoff
            attempts += 1
        except Exception as e:
            last_exception = e
            logger.error(f"Unexpected error connecting to the database: {str(e)}")
            break
    
    # If we get here, all retries failed
    error_msg = f"Failed to connect to the database after {max_retries} attempts. Last error: {str(last_exception)}"
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Create the database engine
engine = create_db_engine()

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
