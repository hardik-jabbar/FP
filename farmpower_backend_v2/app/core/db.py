import os
import socket
import time
import logging
import random
import urllib3
import dns.resolver
from typing import Any, Dict, Generator, List, Optional, Union
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

# Global flag to track if we've already patched the socket
_socket_patched = False

def patch_socket_for_ipv4():
    """Monkey patch socket to force IPv4 and prevent IPv6 usage."""
    global _socket_patched
    if _socket_patched:
        return
        
    original_socket = socket.socket
    
    def patched_socket(family=socket.AF_INET, *args, **kwargs):
        # Force IPv4
        family = socket.AF_INET
        return original_socket(family, *args, **kwargs)
    
    socket.socket = patched_socket
    
    # Also patch getaddrinfo to prefer IPv4
    original_getaddrinfo = socket.getaddrinfo
    
    def getaddrinfo_ipv4(host, port, family=0, *args, **kwargs):
        # Force IPv4
        family = socket.AF_INET
        try:
            return original_getaddrinfo(host, port, family, *args, **kwargs)
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for {host}:{port}: {e}")
            raise
    
    socket.getaddrinfo = getaddrinfo_ipv4
    _socket_patched = True
    logger.info("Patched socket to force IPv4")

# Apply socket patches
patch_socket_for_ipv4()

# SQLAlchemy imports
from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session, sessionmaker, Session as DBSession, declarative_base

# SQLAlchemy Base class for models
Base = declarative_base()

# Export Base for use in models
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db']

# Get database URL from environment variables
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Disable IPv6 for all connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Save the original getaddrinfo
original_getaddrinfo = socket.getaddrinfo

def patched_getaddrinfo(*args, **kwargs):
    # Force IPv4 for all DNS lookups
    kwargs['family'] = socket.AF_INET
    return original_getaddrinfo(*args, **kwargs)

# Apply the patch
socket.getaddrinfo = patched_getaddrinfo

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
    # First try: Direct IP address (no resolution needed)
    try:
        socket.inet_pton(socket.AF_INET, hostname)
        return {"host": hostname, "port": port, "family": socket.AF_INET}
    except (socket.error, ValueError):
        pass  # Not a direct IP, continue with resolution
    
    # Second try: System getaddrinfo with forced IPv4
    try:
        addrinfo = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        if addrinfo:
            return {"host": addrinfo[0][4][0], "port": port, "family": socket.AF_INET}
    except (socket.gaierror, socket.herror) as e:
        logger.warning(f"System DNS resolution failed for {hostname}:{port}: {e}")
    
    # Third try: dnspython with Google DNS
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google DNS
        resolver.timeout = 2
        resolver.lifetime = 5
        
        # Try A records (IPv4)
        try:
            answers = resolver.resolve(hostname, 'A')
            if answers:
                return {"host": str(answers[0]), "port": port, "family": socket.AF_INET}
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
            
        # Try CNAME
        try:
            cname = resolver.resolve(hostname, 'CNAME')
            if cname:
                return resolve_host_to_ip(str(cname[0].target), port)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
            
    except Exception as e:
        logger.warning(f"DNS resolution with dnspython failed for {hostname}:{port}: {e}")
    
    # Final fallback: Hardcoded IP if hostname matches known Supabase pattern
    if "db.supabase.com" in hostname:
        logger.warning(f"Using hardcoded IP for Supabase as last resort")
        return {"host": "35.239.129.36", "port": port, "family": socket.AF_INET}
    
    raise ValueError(f"Could not resolve {hostname} to an IPv4 address after multiple attempts")

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
    
    last_error = None
    retry_delay = initial_retry_delay
    max_retry_delay = 30  # Maximum 30 seconds between retries
    
    for attempt in range(max_retries):
        try:
            # Try to resolve host to IP on each attempt
            try:
                resolved = resolve_host_to_ip(original_host, port)
                host = resolved["host"]
                logger.info(f"Resolved {original_host} to {host} (attempt {attempt + 1})")
                
                # Rebuild URL with resolved IP
                netloc = f"{parsed_url.username}:{parsed_url.password}@{host}:{port}"
                parsed_url = parsed_url._replace(netloc=netloc)
                db_url_resolved = urlunparse(parsed_url)
                
                # Force IPv4 in connection args
                connect_args["hostaddr"] = host
                
            except Exception as resolve_error:
                logger.error(f"DNS resolution failed: {resolve_error}")
                # If resolution fails, try with original URL as last resort
                db_url_resolved = SQLALCHEMY_DATABASE_URL
                if "hostaddr" in connect_args:
                    del connect_args["hostaddr"]
            
            # Create engine with current settings
            engine = create_engine(
                db_url_resolved,
                pool_pre_ping=True,
                pool_recycle=300,  # Recycle connections after 5 minutes
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                connect_args=connect_args,
                # Disable connection pooling during connection testing
                poolclass=None if attempt == 0 else None
            )
            
            # Test the connection with a simple query
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    raise Exception("Test query did not return expected result")
            
            logger.info("Successfully connected to the database")
            return engine
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Calculate next retry delay with exponential backoff and jitter
                retry_delay = min(retry_delay * 2, max_retry_delay)
                jitter = random.uniform(0.8, 1.2)  # Add some randomness
                actual_delay = min(retry_delay * jitter, max_retry_delay)
                
                logger.warning(
                    f"Connection attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                    f"Retrying in {actual_delay:.1f}s..."
                )
                time.sleep(actual_delay)
    
    # If we get here, all retries failed
    error_msg = (
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {str(last_error) if last_error else 'Unknown error'}"
    )
    logger.error(error_msg)
    raise Exception(error_msg)

def get_db() -> Generator[Session, None, None]:
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
