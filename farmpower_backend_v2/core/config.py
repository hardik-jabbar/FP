from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("PGHOST", "db.fmqxdoocmapllbuecblc.supabase.co")
    DB_PORT: int = int(os.getenv("PGPORT", "5432"))
    DB_NAME: str = os.getenv("PGDATABASE", "postgres")
    DB_USER: str = os.getenv("PGUSER", "postgres")
    DB_PASSWORD: str = os.getenv("PGPASSWORD", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    class Config:
        env_file = ".env.production"

settings = Settings()