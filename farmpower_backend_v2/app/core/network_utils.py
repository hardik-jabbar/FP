"""
Network utilities for handling database connections with IPv4/IPv6 issues.
"""

import socket
import logging
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def resolve_hostname_to_ipv4(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IPv4 address, avoiding IPv6 issues.
    
    Args:
        hostname: The hostname to resolve
        
    Returns:
        IPv4 address string or None if resolution fails
    """
    try:
        # Force IPv4 resolution
        ipv4_address = socket.gethostbyname(hostname)
        logger.info(f"✅ Resolved {hostname} to IPv4: {ipv4_address}")
        return ipv4_address
    except socket.gaierror as e:
        logger.error(f"❌ Failed to resolve {hostname} to IPv4: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error resolving {hostname}: {e}")
        return None

def test_connection(hostname: str, port: int, timeout: int = 10) -> bool:
    """
    Test if a hostname:port is reachable.
    
    Args:
        hostname: The hostname to test
        port: The port to test
        timeout: Connection timeout in seconds
        
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        # Try IPv4 first
        ipv4_address = resolve_hostname_to_ipv4(hostname)
        if ipv4_address:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ipv4_address, port))
            sock.close()
            
            if result == 0:
                logger.info(f"✅ Connection test successful: {ipv4_address}:{port}")
                return True
            else:
                logger.warning(f"⚠️ Connection test failed: {ipv4_address}:{port} (error: {result})")
        else:
            logger.warning(f"⚠️ Could not resolve {hostname} to IPv4")
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Connection test error: {e}")
        return False

def get_supabase_connection_info(connection_string: str) -> Tuple[str, str, int, str, str]:
    """
    Parse Supabase connection string and return connection components.
    
    Args:
        connection_string: The database connection string
        
    Returns:
        Tuple of (hostname, ipv4_address, port, database, username)
    """
    try:
        # Parse the connection string
        # Format: postgresql://username:password@hostname:port/database
        if '://' in connection_string:
            parts = connection_string.split('://')[1]
            if '@' in parts:
                auth_part, host_part = parts.split('@', 1)
                username = auth_part.split(':')[0]
                
                if '/' in host_part:
                    host_port, database = host_part.split('/', 1)
                    if ':' in host_port:
                        hostname, port = host_port.split(':')
                        port = int(port)
                    else:
                        hostname = host_port
                        port = 5432
                else:
                    hostname = host_part
                    port = 5432
                    database = 'postgres'
            else:
                raise ValueError("Invalid connection string format")
        else:
            raise ValueError("Invalid connection string format")
        
        # Resolve to IPv4
        ipv4_address = resolve_hostname_to_ipv4(hostname)
        
        return hostname, ipv4_address, port, database, username
        
    except Exception as e:
        logger.error(f"❌ Error parsing connection string: {e}")
        return None, None, None, None, None

def create_ipv4_connection_string(original_string: str) -> str:
    """
    Create an IPv4-only connection string from the original.
    
    Args:
        original_string: The original connection string
        
    Returns:
        Modified connection string with IPv4 address
    """
    try:
        hostname, ipv4_address, port, database, username = get_supabase_connection_info(original_string)
        
        if ipv4_address:
            # Reconstruct the connection string with IPv4 address
            # Extract password from original string
            if '://' in original_string and '@' in original_string:
                auth_part = original_string.split('://')[1].split('@')[0]
                if ':' in auth_part:
                    password = auth_part.split(':', 1)[1]
                    new_string = f"postgresql://{username}:{password}@{ipv4_address}:{port}/{database}"
                    logger.info(f"✅ Created IPv4 connection string: postgresql://{username}:***@{ipv4_address}:{port}/{database}")
                    return new_string
        
        logger.warning("⚠️ Could not create IPv4 connection string, returning original")
        return original_string
        
    except Exception as e:
        logger.error(f"❌ Error creating IPv4 connection string: {e}")
        return original_string
