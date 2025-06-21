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
    """Create a database engine with retry logic and better error handling."""
    attempts = 0
    last_exception = None
    
    # Log the database URL (masked) for debugging
    db_url = SQLALCHEMY_DATABASE_URL
    if '@' in db_url:
        # Mask the password in the URL for logging
        protocol_part = db_url.split('://')[0] + '://'
        creds_and_rest = db_url.split('://', 1)[1]
        if '@' in creds_and_rest:
            creds_part, host_part = creds_and_rest.split('@', 1)
            if ':' in creds_part:
                username_part = creds_part.split(':', 1)[0]
                masked_url = f"{protocol_part}{username_part}:***@{host_part}"
            else:
                masked_url = f"{protocol_part}***@{host_part}"
        else:
            masked_url = f"{protocol_part}***@{creds_and_rest}"
    else:
        masked_url = db_url
    
    logger.info(f"Creating database engine with URL (masked): {masked_url}")
    
    # Configure engine arguments
    engine_args = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,    # Recycle connections after 5 minutes
        "pool_timeout": 30,     # Wait up to 30 seconds for a connection from the pool
        "max_overflow": 20,     # Allow up to 20 connections beyond pool_size
        "pool_size": 5,         # Maintain up to 5 persistent connections
        "echo": True,          # Log SQL queries (useful for debugging)
    }


    # For SQLite, we need to add check_same_thread=False
    if db_url.startswith('sqlite'):
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        # For PostgreSQL, set a statement timeout
        engine_args["connect_args"] = {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"
        }
    
    while attempts < max_retries:
        try:
            logger.info(f"Attempt {attempts + 1}/{max_retries} - Connecting to database")
            
            # Create the engine
            engine = create_engine(db_url, **engine_args)
            
            # Test the connection with a simple query
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("✅ Successfully connected to the database")
                    return engine
                else:
                    raise OperationalError("Test query did not return expected result", None, None)
                
        except OperationalError as e:
            last_exception = e
            logger.warning(f"⚠️ Database connection attempt {attempts + 1} failed: {str(e)}")
            if attempts < max_retries - 1:  # Don't sleep on the last attempt
                wait_time = retry_delay * (attempts + 1)
                logger.info(f"⏳ Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)  # Exponential backoff
            attempts += 1
            
        except Exception as e:
            last_exception = e
            logger.error(f"❌ Unexpected error connecting to the database: {str(e)}")
            logger.exception("Stack trace:")
            break
    
    # If we get here, all retries failed
    error_msg = f"❌ Failed to connect to the database after {max_retries} attempts. " \
               f"Last error: {str(last_exception)}\n" \
               f"Database URL format: {masked_url}"
    
    logger.error(error_msg)
    
    # Provide more detailed error information
    if "Invalid port" in str(last_exception):
        logger.error("⚠️  Check if the port number is correct in your database URL")
    if "password authentication failed" in str(last_exception).lower():
        logger.error("⚠️  Check if the username and password are correct")
    if "does not exist" in str(last_exception).lower():
        logger.error("⚠️  Check if the database name is correct")
    if "could not translate host name" in str(last_exception).lower():
        logger.error("⚠️  Check if the database hostname is correct and accessible")
    
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
