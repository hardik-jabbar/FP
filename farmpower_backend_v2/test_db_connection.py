import os
import sys
from urllib.parse import urlparse

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_database_url():
    """Check and display database URL information."""
    db_url = settings.DATABASE_URL
    print("\n=== Database Connection Test ===")
    print(f"Using database URL: {db_url}")
    
    try:
        parsed = urlparse(db_url)
        print("\nURL Components:")
        print(f"Scheme: {parsed.scheme}")
        print(f"Username: {parsed.username}")
        print(f"Password: {'*' * 8 if parsed.password else 'None'}")
        print(f"Hostname: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path.lstrip('/')}")
        
        if not all([parsed.scheme, parsed.hostname, parsed.path.strip('/')]):
            print("\n⚠️  Warning: Database URL appears to be incomplete or malformed")
        
        if parsed.scheme not in ['postgresql', 'postgres', 'sqlite']:
            print(f"\n⚠️  Warning: Unsupported database type: {parsed.scheme}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error parsing database URL: {str(e)}")
        return False

def test_connection():
    """Test the database connection."""
    from sqlalchemy import create_engine
    from sqlalchemy.exc import SQLAlchemyError
    
    db_url = settings.DATABASE_URL
    print("\n=== Testing Database Connection ===")
    
    try:
        # Create a test engine with a short timeout
        engine = create_engine(
            db_url,
            connect_args={"connect_timeout": 5},
            pool_pre_ping=True
        )
        
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Successfully connected to database!")
            print(f"Database version: {version}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    
    # Check the database URL
    if not check_database_url():
        sys.exit(1)
    
    # Test the connection
    if not test_connection():
        sys.exit(1)
    
    print("\n✅ All tests completed successfully!")
