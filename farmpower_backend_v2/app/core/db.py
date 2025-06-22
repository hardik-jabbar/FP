import logging
import sys
import time
import socket
import ssl
from typing import Generator, Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine, text, URL
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
    db_url = SQLALCHEMY_DATABASE_URL
    parsed_url = urlparse(db_url)
    
    # Mask the password in the URL for logging
    if parsed_url.password:
        masked_url = db_url.replace(parsed_url.password, '***')
    else:
        masked_url = db_url
    
    logger.info(f"Creating database engine with URL: {masked_url}")
    
    # Configure engine arguments
    engine_args = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 30,
        "max_overflow": 20,
        "pool_size": 5,
        "echo": True,
    }
    
    # For SQLite, we need to add check_same_thread=False
    if db_url.startswith('sqlite'):
        engine_args["connect_args"] = {"check_same_thread": False}
        return create_engine(db_url, **engine_args)
    
    # For PostgreSQL connections
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    dbname = parsed_url.path.lstrip('/')
    
    # For Supabase connections
    if "supabase.co" in host:
        logger.info("Supabase host detected, configuring connection")
        
        # Force IPv4 resolution
        try:
            ipv4 = socket.gethostbyname(host)
            logger.info(f"Resolved {host} to IPv4: {ipv4}")
            
            # Create connection URL with IPv4
            connection_url = URL.create(
                'postgresql',
                username=parsed_url.username,
                password=parsed_url.password,
                host=ipv4,
                port=port,
                database=dbname
            )
            
            # Connection arguments
            connect_args = {
                'connect_timeout': 10,
                'sslmode': 'require',
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
                'target_session_attrs': 'read-write',
                'options': '-c search_path=public',
                'gssencmode': 'disable'
            }
            
            # Create engine with retry logic
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Connection attempt {attempt}/{max_retries}")
                    engine = create_engine(
                        connection_url,
                        connect_args=connect_args,
                        **engine_args
                    )
                    
                    # Test the connection
                    with engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    
                    logger.info("Successfully connected to the database")
                    return engine
                    
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Failed to connect after {max_retries} attempts")
                        raise
                    
                    logger.warning(f"Connection attempt {attempt} failed: {str(e)}")
                    time.sleep(retry_delay * (2 ** (attempt - 1)))  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Failed to resolve hostname or create engine: {str(e)}")
            raise
    
    # For non-Supabase PostgreSQL connections
    try:
        # Try to resolve to IPv4
        try:
            host_info = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)
            if host_info:
                ipv4_address = host_info[0][4][0]
                logger.info(f"Resolved {host} to IPv4: {ipv4_address}")
                host = ipv4_address
        except Exception as e:
            logger.warning(f"IPv4 resolution failed for {host}: {e}")
        
        # Create standard PostgreSQL connection
        connection_url = URL.create(
            'postgresql',
            username=parsed_url.username,
            password=parsed_url.password,
            host=host,
            port=port,
            database=dbname
        )
        
        connect_args = {
            'connect_timeout': 30,
            'sslmode': 'require',
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'options': '-c statement_timeout=60000 -c idle_in_transaction_session_timeout=30000'
        }
        
        return create_engine(connection_url, connect_args=connect_args, **engine_args)
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise
        
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
                
                # For Supabase, ensure we're using the correct port
                if "supabase.co" in base_netloc and ":" not in base_netloc:
                    base_netloc = f"{base_netloc}:{SUPABASE_PORT}"
                
                # Reconstruct the URL with proper query parameters
                if query:
                    db_url = f"{parsed_url.scheme}://{base_netloc}?{query}"
                else:
                    db_url = f"{parsed_url.scheme}://{base_netloc}"
                
                # Log connection details (masked)
                if '@' in db_url:
                    # For direct connection strings, mask the password
                    if '://' in db_url and '@' in db_url:
                        scheme_rest = db_url.split('://', 1)
                        auth_host = scheme_rest[1].split('@', 1)
                        if len(auth_host) > 1 and ':' in auth_host[0]:
                            user = auth_host[0].split(':', 1)[0]
                            masked_url = f"{scheme_rest[0]}://{user}:***@{auth_host[1]}"
                            logger.info(f"Connecting to: {masked_url}")
                else:
                    logger.info(f"Connecting to: {db_url}")
                
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
