#!/usr/bin/env python3
"""
Debug script to test database connection and environment variables.
Run this script to diagnose database connection issues.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables."""
    logger.info("=== Environment Variables Check ===")
    
    env_vars = [
        'DATABASE_URL',
        'SQLALCHEMY_DATABASE_URL', 
        'DB_HOST',
        'DB_PORT',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'ENVIRONMENT',
        'HOST',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not Set')
        if 'password' in var.lower() and value != 'Not Set':
            value = '***' + value[-4:] if len(value) > 4 else '***'
        logger.info(f"{var}: {value}")

def test_database_connection():
    """Test database connection."""
    logger.info("=== Database Connection Test ===")
    
    try:
        from app.core.config import settings
        logger.info(f"DATABASE_URL from settings: {settings.DATABASE_URL[:50]}..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL)
        
        from app.core.db import engine, SessionLocal
        
        # Test connection
        db = SessionLocal()
        result = db.execute("SELECT 1 as test")
        test_value = result.scalar()
        db.close()
        
        if test_value == 1:
            logger.info("✅ Database connection successful!")
            return True
        else:
            logger.error("❌ Database connection test failed - unexpected result")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def test_imports():
    """Test importing all modules."""
    logger.info("=== Import Test ===")
    
    try:
        from app import models
        logger.info("✅ Models imported successfully")
        
        from app.core.db import Base, engine, SessionLocal
        logger.info("✅ Database modules imported successfully")
        
        from app.routers import users, tractors, fields, crops
        logger.info("✅ Router modules imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {str(e)}")
        return False

def main():
    """Main debug function."""
    logger.info("🔍 Starting FarmPower Backend Debug...")
    
    # Check environment
    check_environment()
    
    # Test imports
    if not test_imports():
        logger.error("❌ Import test failed - cannot proceed with database test")
        return False
    
    # Test database connection
    if not test_database_connection():
        logger.error("❌ Database connection test failed")
        return False
    
    logger.info("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
