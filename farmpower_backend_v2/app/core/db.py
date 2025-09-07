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

# Check if DATABASE_URL is properly set and not a placeholder
if not SQLALCHEMY_DATABASE_URL or SQLALCHEMY_DATABASE_URL == "<IPv4>" or "placeholder" in SQLALCHEMY_DATABASE_URL:
    error_msg = f"Error: DATABASE_URL environment variable is not properly set: {SQLALCHEMY_DATABASE_URL}"
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    print("Please ensure the database connection string is properly configured in Render.", file=sys.stderr)
    # Don't exit immediately in production - let the app start and handle connection errors gracefully
    if os.getenv('ENVIRONMENT', 'development') == 'production':
        logger.warning("Running in production mode - will attempt to connect later")
        SQLALCHEMY_DATABASE_URL = "postgresql://placeholder:placeholder@placeholder:5432/placeholder"
    else:
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
    
    # Use a local variable to avoid modifying the global
    db_url = SQLALCHEMY_DATABASE_URL
    
    # Connection arguments with aggressive timeouts and keepalives
    connect_args = {
        "connect_timeout": 30,  # Increased timeout for network issues
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=30000"
    }
    
    # Force IPv4 connection for Supabase to avoid IPv6 issues
    if "supabase.co" in db_url:
        connect_args["options"] += " -c tcp_keepalives_idle=30 -c tcp_keepalives_interval=10 -c tcp_keepalives_count=5"
        # Force IPv4 by using the IPv4 address if available
        import socket
        try:
            hostname = db_url.split('@')[1].split(':')[0]
            ipv4_address = socket.gethostbyname(hostname)
            logger.info(f"Resolved {hostname} to IPv4: {ipv4_address}")
            # Replace hostname with IPv4 address in the URL
            db_url = db_url.replace(hostname, ipv4_address)
            logger.info(f"Using IPv4 address for connection: {ipv4_address}")
        except Exception as e:
            logger.warning(f"Could not resolve IPv4 address for {hostname}: {e}")
            # If DNS resolution fails, try using the original URL with IPv4 preference
            logger.info("Using original URL with IPv4 preference settings")
            # Add IPv4 preference to connection args
            connect_args["options"] += " -c preferIPv4=true"
    
    # Force SSL if not explicitly set
    if "sslmode" not in db_url.lower():
        connect_args["sslmode"] = "require"
    
    # Add Supabase-specific settings
    for attempt in range(max_retries):
        try:
            # Create engine with connection pooling and timeouts
            engine = create_engine(
                db_url,  # Use the local db_url variable
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
    
    # If we get here, all retries failed - create engine anyway for startup
    logger.warning("Failed to connect to database during startup, but creating engine for later use")
    engine = create_engine(
        db_url,  # Use the local db_url variable
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    return engine

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

# Create database engine and session with graceful fallback
def create_engine_with_fallback():
    """Create database engine with fallback for startup issues."""
    try:
        if SQLALCHEMY_DATABASE_URL and "placeholder" not in SQLALCHEMY_DATABASE_URL:
            engine = create_db_engine()
            logger.info("✅ Database engine and session created successfully")
            return engine
        else:
            logger.warning("⚠️ Using fallback database engine due to invalid DATABASE_URL")
            return create_engine("sqlite:///./fallback.db")
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {str(e)}")
        logger.warning("⚠️ Using fallback SQLite database for startup")
        return create_engine("sqlite:///./fallback.db")

# Create engine and session
engine = create_engine_with_fallback()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Update exports to include all necessary components
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db', 'Session']
