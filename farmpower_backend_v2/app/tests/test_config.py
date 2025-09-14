import os
import tempfile
from pathlib import Path

# Test specific settings
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["TESTING"] = "True"

# Force SQLite for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DB_HOST"] = ""
os.environ["DB_PORT"] = ""
os.environ["DB_NAME"] = ""
os.environ["DB_USER"] = ""
os.environ["DB_PASSWORD"] = ""

# JWT settings
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

# File upload settings
TEMP_DIR = tempfile.mkdtemp()
os.environ["UPLOAD_DIR"] = TEMP_DIR

# CORS settings
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

# Clean up function for after tests
def cleanup_test_files():
    # Remove temporary files
    if os.path.exists("test.db"):
        os.remove("test.db")
    if os.path.exists(TEMP_DIR):
        for file in Path(TEMP_DIR).glob("*"):
            file.unlink()
        os.rmdir(TEMP_DIR)