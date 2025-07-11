#!/usr/bin/env python3
"""
Test script to verify that the main fixes work correctly.
This script tests the basic imports and configurations.
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all critical imports work."""
    logger.info("Testing imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        logger.info("✅ Config imported successfully")
        
        from app.core.db import Base, engine, SessionLocal
        logger.info("✅ Database modules imported successfully")
        
        from app.models import user, tractor, field, crop
        logger.info("✅ Models imported successfully")
        
        from app.services import user_service
        logger.info("✅ Services imported successfully")
        
        from app.routers import users, tractors, fields
        logger.info("✅ Routers imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    logger.info("Testing database connection...")
    
    try:
        from app.core.db import engine
        
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            if result.scalar() == 1:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database test query failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Check that required settings are available
        assert settings.DATABASE_URL, "DATABASE_URL not set"
        assert settings.SECRET_KEY, "SECRET_KEY not set"
        assert settings.ALGORITHM, "ALGORITHM not set"
        
        logger.info("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting FarmPower Backend Fix Verification...")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Database Connection Test", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 