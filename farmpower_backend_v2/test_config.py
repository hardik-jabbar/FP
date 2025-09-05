#!/usr/bin/env python3
"""
Simple test script to verify configuration without dependencies.
"""

import os
import sys

def test_environment():
    """Test environment variable configuration."""
    print("=== Environment Variables Test ===")
    
    # Test environment variables
    env_vars = [
        'DATABASE_URL',
        'ENVIRONMENT',
        'HOST',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not Set')
        print(f"{var}: {value}")
    
    # Test if we're in production mode
    env = os.getenv('ENVIRONMENT', 'development')
    print(f"\nEnvironment: {env}")
    
    # Test database URL format
    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        if '<IPv4>' in db_url:
            print("❌ DATABASE_URL contains placeholder <IPv4>")
            return False
        elif 'localhost' in db_url and env == 'production':
            print("❌ DATABASE_URL contains localhost in production")
            return False
        else:
            print("✅ DATABASE_URL format looks correct")
            return True
    else:
        print("❌ DATABASE_URL is not set")
        return False

def test_render_config():
    """Test render.yaml configuration."""
    print("\n=== Render Configuration Test ===")
    
    render_file = "../render.yaml"
    if os.path.exists(render_file):
        print("✅ render.yaml exists")
        
        with open(render_file, 'r') as f:
            content = f.read()
            
        if 'fromDatabase:' in content:
            print("✅ Database connection configured from database")
        else:
            print("❌ Database connection not properly configured")
            return False
            
        if 'farmpower-db' in content:
            print("✅ Database name configured correctly")
        else:
            print("❌ Database name not found")
            return False
            
        return True
    else:
        print("❌ render.yaml not found")
        return False

def main():
    """Main test function."""
    print("🔍 Testing FarmPower Backend Configuration...")
    
    env_ok = test_environment()
    config_ok = test_render_config()
    
    if env_ok and config_ok:
        print("\n✅ Configuration looks good!")
        print("\n📋 Next steps:")
        print("1. Deploy to Render")
        print("2. Check the health endpoint: https://your-app.onrender.com/health")
        print("3. Verify database connection in Render logs")
        return True
    else:
        print("\n❌ Configuration issues found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
