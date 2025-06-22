import logging
import sys
import time
import socket
import ssl
import random
from typing import Generator, Optional, List, Union, Dict, Any
from urllib.parse import urlparse, urlunparse, quote_plus, unquote

from sqlalchemy import create_engine, text, URL, exc
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session

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

def resolve_host_to_ip(hostname: str, port: int = 5432) -> List[Dict[str, Any]]:
    """Resolve hostname to IP addresses with timeout and error handling."""
    try:
        # Try to get all IP addresses for the hostname
        addrinfo = socket.getaddrinfo(
            hostname, port,
            family=socket.AF_INET,  # IPv4 only
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        
        # Extract unique IPs
        unique_ips = {}
        for _, _, _, _, (ip, _) in addrinfo:
            if ip not in unique_ips:
                unique_ips[ip] = {
                    'ip': ip,
                    'family': 'ipv4',
                    'priority': 0  # Can be used for prioritization
                }
        
        logger.info(f"Resolved {hostname} to IPs: {list(unique_ips.keys())}")
        return list(unique_ips.values())
        
    except socket.gaierror as e:
        logger.warning(f"DNS resolution failed for {hostname}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error resolving {hostname}: {e}", exc_info=True)
        return []

def test_connection(engine: Engine, max_attempts: int = 3) -> bool:
    """Test database connection with retries."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            last_error = e
            wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10s
            logger.warning(
                f"Connection attempt {attempt}/{max_attempts} failed: {str(e)}. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
    
    logger.error(f"All connection attempts failed. Last error: {str(last_error)}")
    return False

def create_db_engine(max_retries: int = 3, retry_delay: int = 2) -> Engine:
    """
    Create a database engine with robust connection handling.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Initial delay between retries in seconds
        
    Returns:
        SQLAlchemy Engine instance
        
    Raises:
        Exception: If all connection attempts fail
    """
    # Get database URL from settings
    db_url = settings.DATABASE_URL
    parsed_url = urlparse(db_url)
    
    # Mask password for logging
    safe_url = db_url
    if parsed_url.password:
        safe_url = db_url.replace(parsed_url.password, '***')
    
    logger.info(f"Initializing database connection to: {safe_url}")
    
    # Configure engine parameters
    engine_args: Dict[str, Any] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,  # Recycle connections after 5 minutes
        "pool_timeout": 30,   # Wait up to 30s for a connection from the pool
        "max_overflow": 10,   # Allow up to 10 connections beyond pool_size
        "pool_size": 5,       # Maintain 5 persistent connections
        "echo": False,        # Set to True for SQL query logging
        "future": True,       # Use SQLAlchemy 2.0 style APIs
    }
    
    # SQLite specific configuration
    if db_url.startswith('sqlite'):
        engine_args.update({
            "connect_args": {"check_same_thread": False},
            "poolclass": None  # SQLite doesn't support connection pooling
        })
        logger.info("Using SQLite database")
        return create_engine(db_url, **engine_args)
    
    # PostgreSQL specific configuration
    host = parsed_url.hostname or 'localhost'
    port = parsed_url.port or 5432
    
    # Common PostgreSQL connection arguments
    connect_args: Dict[str, Any] = {
        'connect_timeout': 10,          # 10 second connection timeout
        'keepalives': 1,               # Enable keepalive
        'keepalives_idle': 30,          # Start sending keepalives after 30s of inactivity
        'keepalives_interval': 10,      # Send keepalives every 10s
        'keepalives_count': 5,          # Consider connection dead after 5 failed keepalives
        'sslmode': 'require',           # Require SSL
        'target_session_attrs': 'read-write',
        'options': '-c statement_timeout=60000',  # 1 minute statement timeout
    }
    
    # For Supabase, try multiple connection methods
    if 'supabase.co' in host:
        logger.info("Supabase host detected, using optimized connection settings")
        
        # Generate all possible connection URLs to try
        connection_urls = []
        
        # 1. Try with hostname first (works in most environments)
        connection_urls.append(get_connection_url(parsed_url))
        
        # 2. Try with resolved IPs
        resolved_ips = resolve_host_to_ip(host, port)
        for ip_info in resolved_ips:
            connection_urls.append(get_connection_url(parsed_url, ip_info['ip'], port))
        
        # 3. Try with common alternative ports if default port fails
        if port == 5432:
            for alt_port in [5433, 5439]:
                connection_urls.append(get_connection_url(parsed_url, host, alt_port))
        
        logger.info(f"Trying {len(connection_urls)} connection methods...")
        
        # Try each connection URL
        for idx, connection_url in enumerate(connection_urls, 1):
            display_url = str(connection_url).replace(
                f":{parsed_url.password}@", 
                f":{'*' * min(3, len(parsed_url.password or ''))}@"
            )
            logger.info(f"Attempting connection {idx}/{len(connection_urls)}: {display_url}")
            
            try:
                # Create engine with connection pooling
                engine = create_engine(
                    connection_url,
                    connect_args=connect_args,
                    **engine_args
                )
                
                # Test the connection
                if test_connection(engine, max_attempts=2):
                    logger.info("Successfully connected to the database")
                    return engine
                
            except Exception as e:
                logger.warning(f"Connection attempt failed: {str(e)}")
                continue
        
        # If we get here, all connection attempts failed
        raise Exception(
            "Failed to connect to Supabase database after trying all methods. "
            "Please check your network connection, database URL, and firewall settings."
        )
    
    # For non-Supabase PostgreSQL connections
    try:
        # Try to resolve hostname to IP
        resolved_ips = resolve_host_to_ip(host, port)
        if resolved_ips:
            # If resolution successful, try connecting to the first IP
            ip = resolved_ips[0]['ip']
            logger.info(f"Using resolved IP address: {ip}")
            connection_url = get_connection_url(parsed_url, ip, port)
        else:
            # Fall back to hostname if resolution fails
            logger.warning(f"Could not resolve {host}, trying with hostname")
            connection_url = get_connection_url(parsed_url, host, port)
        
        # Create and test the connection
        engine = create_engine(connection_url, connect_args=connect_args, **engine_args)
        if test_connection(engine, max_attempts=2):
            return engine
            
        raise Exception("Failed to establish database connection")
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}", exc_info=True)
        raise
        
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
