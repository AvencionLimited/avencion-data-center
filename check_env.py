#!/usr/bin/env python3
"""
Environment and Database Configuration Checker
This script helps verify your environment variables and database configuration
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check environment variables and database configuration"""
    print("🔍 Environment Configuration Check")
    print("=" * 50)
    
    # Load .env file if it exists
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("⚠️ No .env file found")
    
    # Check key environment variables
    env_vars = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Flask secret key',
        'VERCEL': 'Vercel deployment flag'
    }
    
    print("\n📋 Environment Variables:")
    for var, description in env_vars.items():
        value = os.environ.get(var)
        if value:
            if 'password' in var.lower() or 'secret' in var.lower():
                # Mask sensitive values
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {var}: {masked_value} ({description})")
            else:
                print(f"✅ {var}: {value} ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")
    
    # Check database configuration
    print("\n🗄️ Database Configuration:")
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        if 'postgresql://' in database_url:
            print("✅ PostgreSQL database URL detected")
            try:
                import psycopg2
                print("✅ psycopg2 is available")
            except ImportError:
                print("❌ psycopg2 is not available - install with: pip install psycopg2-binary")
        elif 'sqlite://' in database_url:
            print("✅ SQLite database URL detected")
        else:
            print("⚠️ Unknown database type in URL")
    else:
        print("⚠️ No DATABASE_URL set - will use default SQLite file")
    
    # Check if running on Vercel
    print("\n🌐 Deployment Environment:")
    if os.environ.get('VERCEL'):
        print("✅ Running on Vercel")
    else:
        print("✅ Running locally")
    
    print("\n" + "=" * 50)
    print("Configuration check complete!")

if __name__ == "__main__":
    check_environment() 