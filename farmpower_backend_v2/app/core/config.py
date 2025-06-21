import os
import urllib.parse
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Looks for .env in current working directory or parent directories

def get_database_url() -> str:
    """Get and properly format the database URL with URL-encoded credentials."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # If it's a SQLite URL, ensure it's properly formatted
    if db_url.startswith("sqlite"):
        if not db_url.startswith("sqlite:///"):
            db_url = "sqlite:///" + db_url.split("sqlite")[-1].lstrip(":/\\")
        return db_url
    
    # For non-SQLite URLs, ensure proper URL encoding
    if '://' in db_url:
        # Parse the URL
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(db_url)
        
        # Rebuild the URL with encoded components
        netloc = parsed.netloc
        if '@' in netloc:
            # Extract and encode the auth part
            auth, host = netloc.split('@', 1)
            if ':' in auth:
                username, password = auth.split(':', 1)
                # URL encode the username and password
                username = urllib.parse.quote_plus(username)
                password = urllib.parse.quote_plus(password)
                auth = f"{username}:{password}"
            netloc = f"{auth}@{host}"
            
        # Rebuild the URL
        return urlunparse(parsed._replace(netloc=netloc))
    
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
