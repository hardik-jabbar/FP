import os
import secrets
import logging
import sys
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import AnyHttpUrl, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlparse, urlunparse, quote_plus, unquote

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Find and load .env file
env_path = find_dotenv(usecwd=True)
if not env_path:
    env_path = Path(__file__).parent.parent.parent / '.env'

load_dotenv(env_path)

def format_database_url(url: str) -> str:
    """Format and validate a database URL."""
    if url.startswith('sqlite:'):
        if not url.startswith('sqlite:///'):
            url = 'sqlite:///' + url.split('sqlite:')[-1].lstrip(':/\\')
        return url
    
    # Handle PostgreSQL URLs
    if not url.startswith('postgresql://'):
        url = f'postgresql://{url}'
    
    try:
        parsed = urlparse(unquote(url))
        username = quote_plus(parsed.username or '')
        password = quote_plus(parsed.password or '')
        hostname = parsed.hostname or ''
        port = f':{parsed.port}' if parsed.port else ''
        path = parsed.path
        
        netloc = f'{username}:{password}@{hostname}{port}' if password else f'{username}@{hostname}{port}'
        return urlunparse(parsed._replace(netloc=netloc))
    except Exception as e:
        logger.error(f'Error formatting database URL: {str(e)}')
        return url

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FarmPower"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = "INFO"

    # Testing flag
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "farmpower")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def set_database_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Set and validate the database URL."""
        # Use SQLite for testing
        if os.getenv("TESTING", "").lower() == "true":
            return "sqlite:///./test.db"
            
        # Use provided DATABASE_URL or construct from components
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            db_url = f"postgresql://{values['DB_USER']}:{values['DB_PASSWORD']}@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
            
        # Format and validate the URL
        return format_database_url(db_url)

    # Alias for backward compatibility
    @property
    def DATABASE_URL(self) -> str:
        return self.SQLALCHEMY_DATABASE_URI
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://celebrated-crumble-e25621.netlify.app",
    ]
    ALLOWED_HOSTS: str = "*"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5000,http://localhost:8080"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5000,http://localhost:8080"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

# Security
SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(64))
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
JWT_ALGORITHM: str = "HS256"
OTP_EXPIRE_MINUTES: int = 15  # 15 minutes    # File Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf"}

    # Supabase Configuration
    NEXT_PUBLIC_SUPABASE_URL: str = "https://fmqxdoocmapllbuecblc.supabase.co"
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-supabase-service-role-key"
    SUPABASE_URL: str = "https://fmqxdoocmapllbuecblc.supabase.co"

    # External Services
    GOOGLE_AI_API_KEY: str = "your-google-ai-api-key"

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-specific-password"
    EMAIL_FROM: str = "noreply@yourdomain.com"

    # Storage Configuration
    STORAGE_TYPE: str = "local"  # Options: local, s3
    AWS_ACCESS_KEY_ID: str = "your-aws-access-key"
    AWS_SECRET_ACCESS_KEY: str = "your-aws-secret-key"
    AWS_STORAGE_BUCKET_NAME: str = "your-bucket-name"
    AWS_S3_REGION: str = "us-east-1"

    # Rate Limiting
    RATE_LIMIT: str = "100/minute"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "allow"

settings = Settings()

# Print environment mode
environment = "testing" if settings.TESTING else settings.ENVIRONMENT
logger.info(f"\n=== Running in {environment.upper()} mode ===")

# Print database configuration
if settings.TESTING:
    logger.info("=== Using SQLite for testing ===")
    logger.info(f"Database URL: sqlite:///./test.db")
else:
    # Mask sensitive information in logs
    db_url = settings.SQLALCHEMY_DATABASE_URI
    if db_url and '@' in db_url:
        masked_url = '***' + db_url[db_url.find('@'):]
        logger.info(f"Database URL: {masked_url}")
    else:
        logger.info("Database URL: [masked]")
