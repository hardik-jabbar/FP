import os
import urllib.parse
import logging
import sys
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Find and load .env file
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = Path(__file__).parent.parent.parent / '.env'
    logger.warning(f"No .env file found, using default at: {env_path}")
else:
    logger.info(f"Loading environment from: {env_path}")

# Load environment variables, overriding any existing ones
load_dotenv(env_path, override=True)

# Debug: Print environment variables and their sources
logger.info("\n=== Environment Variables ===")
for key in ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DATABASE_URL']:
    value = os.getenv(key, 'Not Set')
    source = 'Environment' if key in os.environ and not os.getenv('DOTENV_LOADED') else '.env file'
    logger.info(f"{key}: {value} (from {source})")

# Force local database configuration if not in production
if os.getenv('ENVIRONMENT', 'development') != 'production':
    logger.info("\n=== Forcing local database configuration ===")
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_NAME'] = 'farmpower'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = 'postgres'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/farmpower'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/farmpower'
    
    # Log the forced configuration
    for key in ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DATABASE_URL']:
        logger.info(f"FORCED {key}: {os.getenv(key)}")

def get_database_url() -> str:
    """Get and properly format the database URL with URL-encoded credentials."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # If it's a SQLite URL, ensure it's properly formatted
    if db_url.startswith("sqlite"):
        if not db_url.startswith("sqlite:///"):
            db_url = "sqlite:///" + db_url.split("sqlite")[-1].lstrip(":/\\")
        return db_url
    
    # Log the original URL (without password) for debugging
    import logging
    logger = logging.getLogger(__name__)
    safe_url = db_url.split('@')[-1] if '@' in db_url else db_url
    logger.info(f"Original database URL format (host only): postgresql://...@{safe_url}")
    
    try:
        # For non-SQLite URLs, ensure proper URL encoding
        if '://' not in db_url:
            db_url = f"postgresql://{db_url}"
            
        from urllib.parse import urlparse, urlunparse, quote_plus, unquote
        
        # First, unquote any URL-encoded parts to handle them properly
        unquoted_url = unquote(db_url)
        
        # Parse the URL
        parsed = urlparse(unquoted_url)
        
        # Extract and encode credentials if they exist
        if parsed.username or parsed.password:
            username = quote_plus(parsed.username or '')
            password = quote_plus(parsed.password or '')
            
            # Handle special characters in password that might break URL parsing
            # Replace any remaining special characters with URL-encoded versions
            password = password.replace('[', '%5B').replace(']', '%5D')
            
            # Rebuild the netloc with encoded credentials
            hostname = parsed.hostname or ''
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"{username}:{password}@{hostname}{port}" if password else f"{username}@{hostname}{port}"
            
            # Rebuild the URL with the new netloc
            db_url = urlunparse(parsed._replace(netloc=netloc))
            
            # Log the final URL (with masked password) for debugging
            masked_url = db_url.replace(password, '***')
            logger.info(f"Final database URL (masked): {masked_url}")
            
    except Exception as e:
        logger.error(f"Error processing database URL: {str(e)}")
        # Return the original URL if parsing fails
        return db_url
    
    return db_url

class Settings:
    # Get the properly formatted database URL
    DATABASE_URL: str = get_database_url()

    # JWT settings
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY", "your-very-secret-key-that-should-be-in-env") # Default for safety, but should be in .env
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # AWS S3 settings - with default fallbacks for local development
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID", "dummy_access_key")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY", "dummy_secret_key")
    AWS_S3_BUCKET_NAME: Optional[str] = os.getenv("AWS_S3_BUCKET_NAME", "dummy-bucket-name")
    AWS_S3_REGION_NAME: Optional[str] = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

    # Example for other settings that might be added later
    # API_V1_STR: str = "/api/v1"

settings = Settings()
