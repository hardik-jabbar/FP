import logging
import sys
import time
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if not SQLALCHEMY_DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    print("Error: DATABASE_URL environment variable is not set.", file=sys.stderr)
    print("Please create a .env file or set the environment variable.", file=sys.stderr)
    sys.exit(1)

# Connection pool settings
POOL_SIZE = 5
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30  # seconds
POOL_RECYCLE = 3600  # Recycle connections after 1 hour
CONNECT_TIMEOUT = 10  # seconds
STATEMENT_TIMEOUT = 30  # seconds

# Common engine parameters
engine_params = {
    "pool_size": POOL_SIZE,
    "max_overflow": MAX_OVERFLOW,
    "pool_timeout": POOL_TIMEOUT,
    "pool_recycle": POOL_RECYCLE,
    "pool_pre_ping": True,  # Enable connection health checks
    "connect_args": {
        "connect_timeout": CONNECT_TIMEOUT,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
}

# SQLite specific configuration
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    engine_params["connect_args"]["check_same_thread"] = False
    logger.info("Using SQLite database with thread check disabled")
else:
    # PostgreSQL specific configuration
    engine_params["connect_args"].update({
        "options": f"-c statement_timeout={STATEMENT_TIMEOUT * 1000}",  # milliseconds
    })
    logger.info("Using PostgreSQL database with connection pooling")

def create_db_engine():
    """Create and configure SQLAlchemy engine with retry logic."""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_params)
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                
            logger.info("Successfully connected to the database")
            return engine
            
        except OperationalError as e:
            logger.warning(
                f"Database connection attempt {attempt + 1}/{max_retries} failed: {str(e)}"
            )
            if attempt == max_retries - 1:  # Last attempt
                logger.error("Max retries reached. Could not connect to the database.")
                raise
            
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    # If all retries failed
    raise RuntimeError("Failed to connect to the database after multiple attempts")

# Create the engine
engine = create_db_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session with proper cleanup."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        if db:
            db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

# Optional: Add event listeners for connection lifecycle events
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, params, context, executemany):
    """Log SQL queries for debugging."""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Executing query: %s", statement)

@event.listens_for(Engine, "handle_error")
def handle_error(exception_context):
    """Log database errors."""
    exception = exception_context.original_exception
    logger.error("Database error occurred: %s", str(exception))