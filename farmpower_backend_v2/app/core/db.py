import logging
import sys
import time
import socket
import ssl
import random
import urllib3
from typing import Generator, Optional, List, Union, Dict, Any, Tuple
from urllib.parse import urlparse, urlunparse, quote_plus, unquote

# Disable IPv6 for all connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
socket.AF_UNSPEC = socket.AF_INET  # Force IPv4 only

# Monkey patch socket.getaddrinfo to force IPv4
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return socket.getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Apply the patch
socket.getaddrinfo = getaddrinfo_ipv4

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
    """Resolve hostname to IPv4 addresses with timeout and error handling."""
    try:
        logger.info(f"🔍 Attempting DNS resolution for {hostname}:{port}")
        
        # Try system's default DNS resolution first with IPv4
        try:
            # Force IPv4 resolution
            ip = socket.gethostbyname_ex(hostname)[2][0]
            logger.info(f"✅ System DNS resolved {hostname} to {ip}")
            return [{'ip': ip, 'family': 'ipv4', 'priority': 0}]
        except (socket.gaierror, IndexError) as e:
            logger.warning(f"⚠️ System DNS resolution failed for {hostname}: {e}")
        
        # Fall back to getaddrinfo with specific parameters
        try:
            # Force IPv4 only
            addrinfo = socket.getaddrinfo(
                hostname, port,
                family=socket.AF_INET,  # Force IPv4 only
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
                flags=socket.AI_ADDRCONFIG | socket.AI_V4MAPPED
            )
            
            # Extract unique IPv4 addresses
            unique_ips = {}
            for family, socktype, proto, _, sockaddr in addrinfo:
                if family == socket.AF_INET:  # Double check it's IPv4
                    ip = sockaddr[0]
                    if ip not in unique_ips:
                        unique_ips[ip] = {
                            'ip': ip,
                            'family': 'ipv4',
                            'priority': 0
                        }
            
            if not unique_ips:
                logger.warning(f"⚠️ No IPv4 addresses found for {hostname}")
                return []
                
            logger.info(f"✅ getaddrinfo resolved {hostname} to IPv4 addresses: {list(unique_ips.keys())}")
            return list(unique_ips.values())
            
        except Exception as e:
            logger.warning(f"⚠️ getaddrinfo resolution failed for {hostname}: {e}")
            
        # If we get here, all resolution attempts failed
        logger.error(f"❌ All DNS resolution attempts failed for {hostname}")
        return []
        
    except Exception as e:
        logger.error(f"❌ Unexpected error resolving {hostname}: {e}", exc_info=True)
        return []

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
    
    # Configure engine parameters with more aggressive timeouts
    engine_args: Dict[str, Any] = {
        "pool_pre_ping": True,          # Check connections before using them
        "pool_recycle": 300,            # Recycle connections after 5 minutes
        "pool_timeout": 15,             # Wait up to 15s for a connection from the pool
        "max_overflow": 5,              # Allow up to 5 connections beyond pool_size
        "pool_size": 5,                 # Maintain 5 persistent connections
        "echo": False,                  # Set to True for SQL query logging
        "future": True,                 # Use SQLAlchemy 2.0 style APIs
    }
    
    # Common PostgreSQL connection arguments
    connect_args: Dict[str, Any] = {
        'connect_timeout': 10,        # 10 second connection timeout
        'keepalives': 1,              # Enable keepalive
        'keepalives_idle': 30,        # Start sending keepalives after 30s of inactivity
        'keepalives_interval': 10,    # Send keepalives every 10s
        'keepalives_count': 5,        # Consider connection dead after 5 failed keepalives
        'sslmode': 'require',         # Require SSL
        'options': f'-c statement_timeout=30000 -c connect_timeout=10 -c keepalives=1 -c keepalives_idle=30 -c keepalives_interval=10 -c keepalives_count=5',
        'sslrootcert': '/etc/ssl/certs/ca-certificates.crt',  # Use system CA certs
        'target_session_attrs': 'read-write',  # Ensure we connect to a writable primary
        'gssencmode': 'disable',      # Disable GSS encryption
        'sslmode': 'verify-full',     # Verify server certificate
        'application_name': 'farmpower-backend',
    }
    
    # Force IPv4 for all connections
    if hasattr(socket, 'AF_INET6'):
        # Disable IPv6 if available
        socket.AF_INET6 = socket.AF_INET
    
    # Supabase specific configuration
    if 'supabase.co' in host or 'supabase' in host.lower():
        # Force IPv4 for Supabase
        connect_args['gssencmode'] = 'disable'
        connect_args['sslmode'] = 'require'
        connect_args['target_session_attrs'] = 'read-write'
        
        # Add more aggressive timeouts for Supabase
        connect_args['connect_timeout'] = 15
        connect_args['keepalives_idle'] = 60
        connect_args['keepalives_interval'] = 15
        connect_args['keepalives_count'] = 3
        connect_args['options'] = '-c statement_timeout=60000 -c idle_in_transaction_session_timeout=60000'
    
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
    
    # For Supabase, try multiple connection methods with retries
    if 'supabase.co' in host:
        logger.info("Supabase host detected, using optimized connection settings")
        
        # Generate all possible connection URLs to try
        connection_strategies = []
        
        # 1. Try with hostname first (works in most environments)
        connection_strategies.append((
            lambda: get_connection_url(parsed_url),
            'hostname',
            connect_args
        ))
        
        # 2. Try with resolved IPs (IPv4 only)
        resolved_ips = resolve_host_to_ip(host, port)
        for ip_info in resolved_ips:
            if ip_info['family'] == 'ipv4':  # Only use IPv4
                ip_connect_args = connect_args.copy()
                ip_connect_args['hostaddr'] = ip_info['ip']  # Force specific IP
                connection_strategies.append((
                    lambda ip=ip_info['ip']: get_connection_url(parsed_url, ip, port),
                    f'resolved_ipv4_{ip_info["ip"]}',
                    ip_connect_args
                ))
        
        # 3. Try with common alternative ports if default port fails
        if port == 5432:
            for alt_port in [5433, 5439]:
                port_connect_args = connect_args.copy()
                connection_strategies.append((
                    lambda p=alt_port: get_connection_url(parsed_url, host, p),
                    f'alt_port_{alt_port}',
                    port_connect_args
                ))
        
        # Try each connection strategy with retries
        last_error = None
        for strategy in connection_strategies:
            get_url_fn, method, strategy_connect_args = strategy
            
            for attempt in range(max_retries):
                try:
                    # Get the URL for this attempt
                    connection_url = get_url_fn()
                    
                    # Mask password for logging
                    display_url = str(connection_url).replace(
                        f":{parsed_url.password}@", 
                        f":{'*' * min(3, len(parsed_url.password or ''))}@"
                    )
                    
                    logger.info(f"Attempt {attempt + 1}/{max_retries} ({method}): {display_url}")
                    
                    # Create engine with connection pooling
                    engine = create_engine(
                        connection_url,
                        connect_args=strategy_connect_args,
                        **engine_args
                    )
                    
                    # Test the connection with a simple query
                    if test_connection(engine, max_attempts=1):
                        logger.info(f"✅ Successfully connected to the database using {method}")
                        return engine
                    
                except Exception as e:
                    last_error = e
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"⚠️ Connection attempt failed ({method}): {str(e)}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # If we get here, all connection attempts failed
        error_msg = (
            "❌ Failed to connect to Supabase database after all attempts.\n"
            "\nPossible causes:\n"
            "1. Network connectivity issues\n"
            "2. Incorrect database URL or credentials\n"
            f"3. Firewall blocking the connection to {host}\n"
            "4. Supabase service might be down or rate limiting\n"
            "\nTroubleshooting steps:\n"
            "- Verify your internet connection\n"
            "- Check if the database URL is correct\n"
            "- Try accessing the database from a different network\n"
            f"- Check Supabase dashboard for any service disruptions\n"
            f"\nLast error: {str(last_error) if last_error else 'Unknown error'}"
        )
        logger.error(error_msg)
        raise Exception(error_msg) from last_error
    
    # For non-Supabase PostgreSQL connections
    try:
        last_error = None
        
        # Try to resolve hostname to IP first
        resolved_ips = resolve_host_to_ip(host, port)
        connection_urls = []
        
        if resolved_ips:
            # Try resolved IPs first
            for ip_info in resolved_ips:
                if ip_info['family'] == 'ipv4':
                    connection_urls.append((
                        get_connection_url(parsed_url, ip_info['ip'], port),
                        f'resolved_ipv4_{ip_info["ip"]}'
                    ))
        
        # Always try with hostname as fallback
        connection_urls.append((
            get_connection_url(parsed_url, host, port),
            'hostname'
        ))
        
        # Try each connection URL with retries
        for connection_url, method in connection_urls:
            for attempt in range(max_retries):
                try:
                    # Mask password for logging
                    display_url = str(connection_url).replace(
                        f":{parsed_url.password}@", 
                        f":{'*' * min(3, len(parsed_url.password or ''))}@"
                    )
                    logger.info(f"Attempt {attempt + 1}/{max_retries} ({method}): {display_url}")
                    
                    # Create engine with connection pooling
                    engine = create_engine(
                        connection_url,
                        connect_args=connect_args,
                        **engine_args
                    )
                    
                    # Test the connection with a simple query
                    if test_connection(engine, max_attempts=1):
                        logger.info(f"✅ Successfully connected to the database using {method}")
                        return engine
                        
                except Exception as e:
                    last_error = e
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"⚠️ Connection attempt failed ({method}): {str(e)}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # If we get here, all connection attempts failed
        error_msg = (
            f"❌ Failed to connect to PostgreSQL database at {host}:{port} after {max_retries} attempts.\n"
            f"Last error: {str(last_error) if last_error else 'Unknown error'}"
        )
        logger.error(error_msg)
        raise Exception(error_msg) from last_error
        
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {str(e)}", exc_info=True)
        raise
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
