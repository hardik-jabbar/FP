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
    import socket
    from urllib.parse import urlparse, urlunparse, quote_plus, unquote, parse_qs, urlencode
    
    attempts = 0
    last_exception = None
    
    # Log the database URL (masked) for debugging
    db_url = SQLALCHEMY_DATABASE_URL
    
    # Parse the database URL to modify connection parameters
    parsed_url = urlparse(db_url)
    
    # Mask the password in the URL for logging
    if parsed_url.password:
        netloc = f"{parsed_url.username}:***@{parsed_url.hostname}"
        if parsed_url.port:
            netloc += f":{parsed_url.port}"
        masked_url = urlunparse(parsed_url._replace(netloc=netloc))
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
        # For PostgreSQL, set connection parameters
        # Connection parameters - use a dictionary that we'll update conditionally
        connect_args = {}
        
        # Only add parameters that aren't already in the URL
        if '?' not in db_url:
            connect_args.update({
                "connect_timeout": 30,  # Increased timeout for initial connection
                "options": "-c statement_timeout=60000 -c idle_in_transaction_session_timeout=30000",
                "keepalives": 1,  # Enable keepalive
                "keepalives_idle": 30,  # Idle time before sending keepalive
                "keepalives_interval": 10,  # Interval between keepalives
                "keepalives_count": 5,  # Number of keepalive failures before closing
                "sslmode": "require"  # Ensure SSL is used
            })
        else:
            logger.info("Using connection parameters from URL")
        
        # Parse the hostname and handle IPv4/IPv6
        host = parsed_url.hostname
        
        # For Supabase, use the connection pooler
        if "supabase.co" in host:
            logger.info("Supabase host detected, configuring connection pooler")
            # Extract the project reference from the hostname (db.xxx.supabase.co -> xxx)
            project_ref = host.split('.')[1]
            # Use the Supabase connection pooler
            host = f"aws-0-{project_ref}.pooler.supabase.com"
            logger.info(f"Using Supabase connection pooler: {host}")
            
            # Add connection parameters for Supabase
            connection_params = [
                "connect_timeout=30",
                "sslmode=require",
                "options=--application_name=render_app",
                "keepalives=1",
                "keepalives_idle=30",
                "keepalives_interval=10",
                "keepalives_count=5",
                "options=-c statement_timeout=60000"
            ]
            host = f"{host}?{'&'.join(connection_params)}"
        else:
            # For non-Supabase hosts, try to resolve to IPv4
            try:
                host_info = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)
                if host_info:
                    ipv4_address = host_info[0][4][0]
                    logger.info(f"Resolved {host} to IPv4: {ipv4_address}")
                    host = ipv4_address
            except Exception as e:
                logger.warning(f"IPv4 resolution failed for {host}: {e}")
            
            # Add standard connection parameters
            connection_params = [
                "connect_timeout=30",
                "keepalives=1",
                "keepalives_idle=30",
                "keepalives_interval=10",
                "keepalives_count=5",
                "sslmode=require",
                "options=-c statement_timeout=60000"
            ]
            if '?' not in host:  # Don't add params if they're already in the host
                host = f"{host}?{'&'.join(connection_params)}"
        
        # URL encode username and password
        from urllib.parse import quote_plus, unquote
        
        # Handle the case where host might have query parameters
        if '?' in host:
            host, query = host.split('?', 1)
            # Ensure the query parameters are properly encoded
            query = '&'.join(f"{k}={quote_plus(v)}" for param in query.split('&') 
                           for k, v in [param.split('=', 1) if '=' in param else (param, '')])
            host = f"{host}?{query}"
        
        # Decode and re-encode username and password to handle any special characters
        username = quote_plus(unquote(parsed_url.username or ''))
        password = quote_plus(unquote(parsed_url.password or ''))
        
        # Rebuild the URL with the resolved host and encoded credentials
        netloc = f"{username}:{password}@{host}"
        if parsed_url.port:
            netloc += f":{parsed_url.port}"
            
        db_url = urlunparse(parsed_url._replace(netloc=netloc))
        logger.info(f"Using database URL with resolved host: {db_url.split('@')[-1]}")
        
        engine_args["connect_args"] = connect_args
    
    while attempts < max_retries:
        try:
            logger.info(f"Attempt {attempts + 1}/{max_retries} - Connecting to database")
            
            # Rebuild the URL with the current host
            try:
                # Parse the netloc to handle potential query parameters
                netloc_parts = netloc.split('?', 1)
                base_netloc = netloc_parts[0]
                query = netloc_parts[1] if len(netloc_parts) > 1 else ''
                
                # For Supabase, ensure we're using the correct port (6543 for connection pooler)
                if "pooler.supabase.com" in base_netloc:
                    if ":" not in base_netloc:  # Only add port if not already specified
                        base_netloc = f"{base_netloc}:6543"
                
                # Reconstruct the URL with proper query parameters
                if query:
                    db_url = f"{parsed_url.scheme}://{base_netloc}?{query}"
                else:
                    db_url = f"{parsed_url.scheme}://{base_netloc}"
                
                # Log the masked URL (without password)
                safe_netloc = base_netloc.split('@')[-1]  # Remove credentials for logging
                logger.info(f"Connecting to: {parsed_url.scheme}://...@{safe_netloc}")
                
                # Log the actual URL being used (masked)
                if '@' in db_url:
                    # Mask the password in the URL
                    scheme_netloc, path = db_url.split('@', 1)
                    if '://' in scheme_netloc:
                        scheme, auth = scheme_netloc.split('://', 1)
                        if ':' in auth:
                            user = auth.split(':', 1)[0]
                            masked_url = f"{scheme}://{user}:***@{path}"
                            logger.debug(f"Full connection URL (masked): {masked_url}")
                
                # Log the actual URL being used for debugging (without password)
                logger.debug(f"Connection string: {db_url.split('@')[0]}@[MASKED]@{db_url.split('@')[1] if '@' in db_url else ''}")
                
                # Create the engine with updated URL
                logger.info(f"Creating engine with URL: {parsed_url.scheme}://...@{safe_netloc}")
                engine = create_engine(db_url, **engine_args)
                
                # Set up connection pool with aggressive recycling
                engine.pool._pool_timeout = 30
                engine.pool._recycle = 300  # Recycle connections after 5 minutes
                
            except Exception as e:
                logger.error(f"Error creating database URL: {e}")
                raise
            
            # Test the connection with a simple query
            with engine.connect() as conn:
                logger.info("Testing database connection...")
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("✅ Successfully connected to the database")
                    logger.info(f"Database version: {conn.dialect.server_version_info}")
                    return engine
                else:
                    raise OperationalError("Test query did not return expected result", None, None)
                
        except OperationalError as e:
            last_exception = e
            logger.warning(f"⚠️ Database connection attempt {attempts + 1} failed: {str(e)}")
            if attempts < max_retries - 1:  # Don't sleep on the last attempt
                wait_time = retry_delay * (2 ** attempts)  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)
            attempts += 1
            
            # If this is the last attempt, try one more time with direct IP if possible
            if attempts == max_retries - 1 and 'hostname' in locals() and host != parsed_url.hostname:
                logger.info("Trying one more time with direct IP connection...")
                netloc = netloc.replace(parsed_url.hostname, host)
                
        except Exception as e:
            last_exception = e
            logger.error(f"❌ Unexpected error connecting to the database: {str(e)}")
            logger.exception("Stack trace:")
            if attempts < max_retries - 1:
                wait_time = retry_delay * (2 ** attempts)
                time.sleep(wait_time)
            attempts += 1
    
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
