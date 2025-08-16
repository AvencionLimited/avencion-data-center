#!/usr/bin/env python3
"""
Vercel Deployment Helper Script for Avencion Data Center
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    required_files = ['app_simple_working.py', 'api/index.py', 'vercel.json', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    
    # Check if Vercel CLI is installed
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
        else:
            print("❌ Vercel CLI not found or not working")
            print("   Install with: npm i -g vercel")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not installed")
        print("   Install with: npm i -g vercel")
        return False
    
    return True

def check_environment_variables():
    """Check if environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    # Check for .env file
    if Path('.env').exists():
        print("✅ .env file found")
        return True
    
    # Check for environment variables
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   These will need to be set in Vercel dashboard after deployment")
        return False
    
    print("✅ Environment variables found")
    return True

def create_env_template():
    """Create a template .env file"""
    print("\n📝 Creating .env template...")
    
    env_content = """# Avencion Data Center Environment Configuration
# Copy this file to .env and configure your values

# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=0

# Database Configuration
# For PostgreSQL (recommended for production)
DATABASE_URL=postgresql://username:password@host:port/database

# For SQLite (development only)
# DATABASE_URL=sqlite:///db_manager.db

# Upload Configuration
MAX_CONTENT_LENGTH=52428800

# Session Configuration
PERMANENT_SESSION_LIFETIME=86400
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.template file")
    print("   Copy this to .env and configure your values")

def test_app_locally():
    """Test the app locally"""
    print("\n🧪 Testing app locally...")
    
    try:
        # Test if the app can be imported
        sys.path.append('.')
        from app_simple_working import app
        
        with app.app_context():
            from app_simple_working import db
            db.create_all()
        
        print("✅ App imports successfully")
        print("✅ Database tables can be created")
        return True
        
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Deploying to Vercel...")
    
    try:
        # Run vercel command
        result = subprocess.run(['vercel', '--prod'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print(result.stdout)
            return True
        else:
            print("❌ Deployment failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def main():
    """Main deployment process"""
    print("🚀 Avencion Data Center - Vercel Deployment Helper")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return
    
    # Check environment variables
    check_environment_variables()
    
    # Create env template if needed
    if not Path('.env').exists():
        create_env_template()
    
    # Test app locally
    if not test_app_locally():
        print("\n❌ Local test failed. Please fix the issues before deploying.")
        return
    
    # Ask user if they want to deploy
    print("\n" + "=" * 50)
    response = input("Ready to deploy to Vercel? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        deploy_to_vercel()
    else:
        print("\n📋 Manual deployment steps:")
        print("1. Run: vercel login")
        print("2. Run: vercel")
        print("3. Follow the prompts")
        print("4. Set environment variables in Vercel dashboard")
        print("5. Run: vercel --prod")
    
    print("\n📚 For more information, see VERCEL_DEPLOYMENT.md")

if __name__ == '__main__':
    main() 