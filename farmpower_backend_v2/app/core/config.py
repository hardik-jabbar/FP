import os
from dotenv import load_dotenv

# Construct the path to the .env file, assuming it's in the project root (farmpower_backend_v2)
# For this script, __file__ is farmpower_backend_v2/app/core/config.py
# So, project_root is two levels up from this file's directory.
# However, load_dotenv() by default looks for .env in the current working directory or its parents.
# If the app runs from farmpower_backend_v2 as CWD, it should find .env.
# For robustness, one could specify the path:
# project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# load_dotenv(dotenv_path=os.path.join(project_dir, ".env"))

load_dotenv() # Looks for .env in current working directory or parent directories

class Settings:
    DATABASE_URL: str | None = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/farmpower")

    # JWT settings
    SECRET_KEY: str | None = os.getenv("SECRET_KEY", "your-very-secret-key-that-should-be-in-env") # Default for safety, but should be in .env
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # AWS S3 settings - with default fallbacks for local development
    AWS_ACCESS_KEY_ID: str | None = os.getenv("AWS_ACCESS_KEY_ID", "dummy_access_key")
    AWS_SECRET_ACCESS_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY", "dummy_secret_key")
    AWS_S3_BUCKET_NAME: str | None = os.getenv("AWS_S3_BUCKET_NAME", "dummy-bucket-name")
    AWS_S3_REGION_NAME: str | None = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

    # Example for other settings that might be added later
    # API_V1_STR: str = "/api/v1"

settings = Settings()
