import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from app.core.db import create_db_engine

def test_connection():
    print("Testing database connection...")
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Successfully connected to the database!")
            print(f"Test query result: {result.scalar()}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to the database: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
