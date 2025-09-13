import os
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus, urlparse, urlunparse

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("PGHOST", "db.fmqxdoocmapllbuecblc.supabase.co")
    DB_PORT: int = int(os.getenv("PGPORT", "5432"))
    DB_NAME: str = os.getenv("PGDATABASE", "postgres")
    DB_USER: str = os.getenv("PGUSER", "postgres")
    DB_PASSWORD: str = os.getenv("PGPASSWORD", "")

    @property
    def DATABASE_URL(self) -> str:
        # Get the raw DATABASE_URL from environment
        raw_url = os.getenv("DATABASE_URL")
        
        if raw_url:
            # Parse the URL
            parsed = urlparse(raw_url)
            
            # Extract components
            username = parsed.username or self.DB_USER
            password = parsed.password or self.DB_PASSWORD
            hostname = parsed.hostname or self.DB_HOST
            port = str(parsed.port or self.DB_PORT)
            database = parsed.path.lstrip('/') or self.DB_NAME

            # Properly encode the password
            encoded_password = quote_plus(password) if password else ""
            
            # Reconstruct the URL without any query parameters
            return f"postgresql://{username}:{encoded_password}@{hostname}:{port}/{database}"
        else:
            # Construct URL from individual components
            encoded_password = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
            return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env.production"

settings = Settings()