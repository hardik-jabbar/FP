import os
import socket
import time
import logging
import random
import urllib3
import dns.resolver
import sys
from typing import Any, Dict, Generator, List, Optional, Union, cast
from urllib.parse import urlparse, urlunparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable IPv6 for all connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Force IPv4 only for all socket operations
socket.AF_INET6 = socket.AF_INET
socket.has_ipv6 = False

# Configure DNS resolver to only return IPv4 addresses
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Use Google DNS

# Save the original socket functions
_original_socket = socket.socket
_original_getaddrinfo = socket.getaddrinfo

def patch_socket_for_ipv4():
    """Monkey patch socket to force IPv4 and prevent IPv6 usage."""
    # Patch socket.socket
    def patched_socket(family=socket.AF_INET, *args, **kwargs):
        # Force IPv4 only
        return _original_socket(socket.AF_INET, *args, **kwargs)
    
    # Patch socket.getaddrinfo
    def patched_getaddrinfo(host, port, family=0, *args, **kwargs):
        # Force IPv4 only
        if family == 0 or family == socket.AF_UNSPEC:
            family = socket.AF_INET
        elif family == socket.AF_INET6:
            # If IPv6 is explicitly requested, still force IPv4
            family = socket.AF_INET
        
        # Remove any existing family from kwargs to avoid duplicates
        kwargs.pop('family', None)
        
        # Call original getaddrinfo with forced IPv4
        return _original_getaddrinfo(host, port, family=family, *args, **kwargs)
    
    # Apply patches
    socket.socket = patched_socket
    socket.getaddrinfo = patched_getaddrinfo
    
    # Disable IPv6 at the socket module level
    socket.has_ipv6 = False
    
    logger.info("Patched socket to force IPv4")

# Apply socket patches
patch_socket_for_ipv4()

# SQLAlchemy imports
from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import sessionmaker, Session as DBSession, declarative_base, Session

# SQLAlchemy Base class for models
Base = declarative_base()

# Export Base for use in models
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db', 'Session']

# Get database URL from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    error_msg = "Error: DATABASE_URL environment variable is not set."
    logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

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

def resolve_host_to_ip(hostname: str, port: int = 5432) -> Dict[str, Any]:
    """Resolve a hostname to its IPv4 address with multiple fallback strategies."""
    if not hostname or hostname == 'localhost':
        return {"host": "127.0.0.1", "port": port, "resolved": False}
    
    # Special handling for Supabase
    if "supabase" in hostname.lower():
        # Try direct connection first (Supabase handles DNS)
        logger.info("Using direct connection to Supabase")
        return {"host": hostname, "port": port, "resolved": False}
    
    # Skip resolution for IP addresses
    try:
        socket.inet_pton(socket.AF_INET, hostname)
        return {"host": hostname, "port": port, "resolved": False}
    except (socket.error, OSError):
        pass
    
    # Try system DNS resolution first with explicit IPv4
    try:
        addr_info = socket.getaddrinfo(hostname, port, family=socket.AF_INET, type=socket.SOCK_STREAM)
        if addr_info:
            ip = addr_info[0][4][0]  # Get the first resolved IP
            logger.info(f"Resolved {hostname} to {ip} using system DNS (IPv4)")
            return {"host": ip, "port": port, "resolved": True}
    except Exception as e:
        logger.warning(f"System DNS resolution failed for {hostname}: {e}")
    
    # If we get here, all resolution attempts failed
    error_msg = f"Failed to resolve {hostname} to an IP address"
    logger.error(error_msg)
    raise ValueError(error_msg)

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
    
    # Ensure socket is patched for IPv4
    patch_socket_for_ipv4()
    
    # Parse the database URL
    parsed_url = urlparse(SQLALCHEMY_DATABASE_URL)
    original_host = parsed_url.hostname or ""
    port = parsed_url.port or 5432
    
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
    connect_args["options"] = "-c default_transaction_isolation=read committed"
    for attempt in range(max_retries):
        try:
            # Try direct connection first (Supabase handles DNS and load balancing)
            if attempt == 0:
                db_url = SQLALCHEMY_DATABASE_URL
                logger.info("Attempting direct connection to database")
            # Fall back to DNS resolution if direct connection fails
            else:
                resolved = resolve_host_to_ip(original_host, port)
                if resolved["resolved"]:
                    netloc = f"{parsed_url.username}:{parsed_url.password}@{resolved['host']}:{port}" \
                            if parsed_url.username else f"{resolved['host']}:{port}"
                    db_url = parsed_url._replace(netloc=netloc).geturl()
                    logger.info(f"Using resolved IP: {resolved['host']} for {original_host}")
                else:
                    db_url = SQLALCHEMY_DATABASE_URL
            
            # Create the engine with optimized settings for Supabase
            engine = create_engine(
                db_url,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=300,  # Recycle connections after 5 minutes
                pool_size=5,  # Maintain up to 5 connections in the pool
                max_overflow=10,  # Allow up to 10 overflow connections
                pool_timeout=30,  # Wait up to 30 seconds for a connection from the pool
                pool_pre_ping_interval=60,  # Check connection health every minute
                connect_args=connect_args,
            )
            
            # Test the connection with a simple query
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
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(wait_time)
    
    # If we get here, all retries failed
    error_msg = (
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {str(last_error) if last_error else 'Unknown error'}"
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
