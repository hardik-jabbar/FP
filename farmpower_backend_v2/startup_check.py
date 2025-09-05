#!/usr/bin/env python3
"""
Startup check script to diagnose database connection issues before starting the main application.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check all environment variables related to database connection."""
    logger.info("🔍 Checking environment variables...")
    
    env_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development')
    }
    
    issues = []
    
    for key, value in env_vars.items():
        if value is None:
            logger.warning(f"⚠️ {key}: Not Set")
            if key in ['DATABASE_URL', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']:
                issues.append(f"Missing {key}")
        else:
            if key == 'DB_PASSWORD':
                logger.info(f"✅ {key}: {'***' + value[-4:] if len(value) > 4 else '***'}")
            elif '<IPv4>' in value or 'placeholder' in value:
                logger.error(f"❌ {key}: {value} (contains placeholder)")
                issues.append(f"{key} contains placeholder value")
            else:
                logger.info(f"✅ {key}: {value}")
    
    return issues

def check_database_config():
    """Check if we can construct a valid database connection."""
    logger.info("🔍 Checking database configuration...")
    
    db_url = os.getenv('DATABASE_URL')
    
    if db_url and '<IPv4>' not in db_url and 'placeholder' not in db_url:
        logger.info("✅ DATABASE_URL looks valid")
        return True
    
    # Try to construct from individual components
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if all([db_host, db_name, db_user, db_password]):
        logger.info("✅ Can construct database URL from individual components")
        return True
    else:
        logger.error("❌ Cannot construct valid database connection")
        return False

def main():
    """Main startup check function."""
    logger.info("🚀 Starting FarmPower Backend Startup Check...")
    
    # Check environment variables
    env_issues = check_environment()
    
    # Check database configuration
    db_ok = check_database_config()
    
    if env_issues:
        logger.error("❌ Environment issues found:")
        for issue in env_issues:
            logger.error(f"  - {issue}")
    
    if not db_ok:
        logger.error("❌ Database configuration issues found")
        logger.error("")
        logger.error("🔧 Troubleshooting steps:")
        logger.error("1. Ensure the 'farmpower-db' database exists in Render")
        logger.error("2. Check that the database is properly linked to your service")
        logger.error("3. Verify the render.yaml configuration")
        logger.error("4. Check Render dashboard for environment variables")
        logger.error("")
        logger.error("📋 Current render.yaml should have:")
        logger.error("  - Database 'farmpower-db' defined")
        logger.error("  - DATABASE_URL from farmpower-db.connectionString")
        logger.error("  - Individual DB_* variables from farmpower-db properties")
        
        return False
    
    logger.info("✅ All checks passed! Starting application...")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ Startup check failed. Please fix the issues above.")
        sys.exit(1)
    else:
        logger.info("✅ Startup check passed. Proceeding with application startup.")
        sys.exit(0)
