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

# Only force local database configuration if DATABASE_URL is not set and we're in development
if os.getenv('ENVIRONMENT', 'development') != 'production' and not os.getenv('DATABASE_URL'):
    logger.info("\n=== Forcing local database configuration (development mode) ===")
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
else:
    logger.info("\n=== Using provided DATABASE_URL (production mode) ===")
    if os.getenv('DATABASE_URL'):
        logger.info(f"Using DATABASE_URL from environment: {os.getenv('DATABASE_URL').split('@')[-1] if '@' in os.getenv('DATABASE_URL', '') else '***'}")

def get_database_url() -> str:
    """Get and properly format the database URL with URL-encoded credentials."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Log the original URL for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Raw DATABASE_URL from environment: {db_url}")
    
    # Check for placeholder values that indicate configuration issues
    if "<IPv4>" in db_url or "placeholder" in db_url:
        logger.warning(f"⚠️ DATABASE_URL contains placeholder value: {db_url}")
        
        # Check if this is a Supabase connection string
        if "supabase.co" in db_url:
            logger.info("🔍 Detected Supabase connection string with placeholder")
            logger.info("Attempting to fix Supabase connection string...")
            
            # Remove the placeholder from the end of the URL
            if "?hostaddr=<IPv4>" in db_url:
                fixed_url = db_url.replace("?hostaddr=<IPv4>", "")
                logger.info(f"✅ Fixed Supabase URL by removing placeholder: {fixed_url}")
            elif "&hostaddr=<IPv4>" in db_url:
                fixed_url = db_url.replace("&hostaddr=<IPv4>", "")
                logger.info(f"✅ Fixed Supabase URL by removing placeholder: {fixed_url}")
            else:
                fixed_url = db_url
                logger.warning("⚠️ Could not automatically fix Supabase URL")
            
            # For Supabase, try to use a more robust connection approach
            try:
                # Add connection parameters to force IPv4 and improve reliability
                if '?' in fixed_url:
                    # URL already has parameters, add IPv4 preference
                    fixed_url += "&preferIPv4=true"
                else:
                    # Add parameters to force IPv4
                    fixed_url += "?preferIPv4=true"
                
                logger.info("✅ Added IPv4 preference to Supabase connection string")
                return fixed_url
            except Exception as e:
                logger.warning(f"⚠️ Could not modify connection string: {e}")
                return fixed_url
        
        logger.error("This indicates the database connection string is not properly configured.")
        logger.error("Attempting to construct connection string from individual components...")
        
        # Try to construct the connection string from individual components
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        logger.info(f"DB_HOST: {db_host}")
        logger.info(f"DB_PORT: {db_port}")
        logger.info(f"DB_NAME: {db_name}")
        logger.info(f"DB_USER: {db_user}")
        logger.info(f"DB_PASSWORD: {'***' if db_password else 'Not Set'}")
        
        if all([db_host, db_name, db_user, db_password]):
            # Construct the connection string
            from urllib.parse import quote_plus
            constructed_url = f"postgresql://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
            logger.info(f"✅ Constructed database URL from components: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
            return constructed_url
        else:
            logger.error("❌ Missing required database components:")
            logger.error(f"  DB_HOST: {'✅' if db_host else '❌'}")
            logger.error(f"  DB_NAME: {'✅' if db_name else '❌'}")
            logger.error(f"  DB_USER: {'✅' if db_user else '❌'}")
            logger.error(f"  DB_PASSWORD: {'✅' if db_password else '❌'}")
            logger.error("Please check:")
            logger.error("1. Database 'farmpower-db' exists in Render")
            logger.error("2. Database is properly linked to the service")
            logger.error("3. Environment variables are set correctly")
            
            # In production, try to use a fallback or exit gracefully
            if os.getenv('ENVIRONMENT', 'development') == 'production':
                logger.warning("⚠️ Using SQLite fallback in production due to invalid DATABASE_URL")
                return "sqlite:///./fallback.db"
            else:
                logger.error("❌ Cannot proceed with invalid DATABASE_URL in development")
                return db_url
    
    # If it's a SQLite URL, ensure it's properly formatted
    if db_url.startswith("sqlite"):
        if not db_url.startswith("sqlite:///"):
            db_url = "sqlite:///" + db_url.split("sqlite")[-1].lstrip(":/\\")
        return db_url
    
    # Log the original URL (without password) for debugging
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
