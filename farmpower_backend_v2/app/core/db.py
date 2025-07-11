import os
import socket
import time
import logging
import sys
from typing import Any, Dict, Generator, Optional, Union
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy imports
from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import sessionmaker, Session as DBSession, declarative_base, Session

# SQLAlchemy Base class for models
Base = declarative_base()

# Export Base for use in models
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db', 'Session']

from app.core.config import settings

# Get the database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if not SQLALCHEMY_DATABASE_URL:
    error_msg = "Error: DATABASE_URL environment variable is not set."
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

def get_connection_url(
    parsed_url: urlparse,
    host_override: Optional[str] = None,
    port_override: Optional[int] = None
) -> URL:
    """Create a database URL from parsed URL with optional host/port overrides."""
    return URL.create(
        'postgresql',
        username=parsed_url.username,
        password=parsed_url.password,
        host=host_override or parsed_url.hostname,
        port=port_override or (parsed_url.port or 5432),
        database=parsed_url.path.lstrip('/')
    )

def test_connection(engine: Engine, max_attempts: int = 3) -> bool:
    """Test database connection with retries."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            start_time = time.time()
            with engine.connect() as conn:
                # Test basic connection
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    elapsed = (time.time() - start_time) * 1000
                    logger.info(f"✅ Database connection test successful ({elapsed:.2f}ms)")
                    
                    # Get database version for debugging
                    try:
                        version = conn.execute(text("SELECT version()")).scalar()
                        logger.info(f"📊 Database version: {version}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get database version: {e}")
                    
                    return True
                else:
                    raise Exception("Test query did not return expected result")
                    
        except Exception as e:
            last_error = e
            wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10s
            logger.warning(
                f"⚠️ Connection test {attempt}/{max_attempts} failed: {str(e)}. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
    
    logger.error(f"❌ All connection tests failed. Last error: {str(last_error)}")
    if hasattr(last_error, 'orig') and last_error.orig:
        logger.error(f"Original error: {last_error.orig}")
    return False

def create_db_engine(max_retries: int = 5, initial_retry_delay: float = 1.0) -> Engine:
    """Create a SQLAlchemy engine with robust connection handling and retries."""
    if not SQLALCHEMY_DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment variables")
    
    # Connection arguments with aggressive timeouts and keepalives
    connect_args = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=30000"
    }
    
    # Force SSL if not explicitly set
    if "sslmode" not in SQLALCHEMY_DATABASE_URL.lower():
        connect_args["sslmode"] = "require"
    
    # Add Supabase-specific settings
    for attempt in range(max_retries):
        try:
            # Create engine with connection pooling and timeouts
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,  # Enable connection health checks
                connect_args=connect_args
            )
            
            # Test the connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    raise Exception("Test query did not return expected result")
            
            logger.info("Database connection successful")
            return engine
            
        except Exception as e:
            wait_time = min(initial_retry_delay * (2 ** attempt), 30)  # Cap at 30s
            error_msg = f"Connection attempt {attempt + 1}/{max_retries} failed: {str(e)}. Retrying in {wait_time:.1f}s..."
            logger.warning(error_msg)
            last_error = e
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(wait_time)
    
    # If we get here, all retries failed
    error_msg = (
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {str(last_error) if 'last_error' in locals() else 'Unknown error'}"
    )
    logger.error(error_msg)
    raise Exception(error_msg)

def get_db() -> Generator[DBSession, None, None]:
    """
    Dependency to get DB session.
    
    Yields:
        Session: A database session
        
    Raises:
        Exception: If there's an error creating or using the session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Create database engine and session
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Update exports to include all necessary components
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db', 'Session']
