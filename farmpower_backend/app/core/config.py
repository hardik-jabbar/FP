import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/defaultdb")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret-key-is-not-secure") # Change this in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Default to 30 minutes

    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME: str | None = os.getenv("AWS_S3_BUCKET_NAME")
    AWS_S3_REGION: str | None = os.getenv("AWS_S3_REGION", "us-east-1") # Default region if not set

    # Add other environment variables here as needed
    # EXAMPLE_API_KEY: str = os.getenv("EXAMPLE_API_KEY")

settings = Settings()
