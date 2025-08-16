#!/usr/bin/env python3
"""
Vercel Deployment Helper Script
This script helps validate your setup before deploying to Vercel.
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    required_files = [
        'vercel.json',
        'api/index.py',
        'app_vercel.py',
        'requirements-simple.txt',
        'templates/base.html',
        'templates/login.html',
        'templates/index.html'
    ]
    
    print("🔍 Checking required files...")
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found!")
    return True

def check_requirements():
    """Check if requirements file has necessary dependencies"""
    print("\n🔍 Checking requirements.txt...")
    
    if not os.path.exists('requirements-simple.txt'):
        print("❌ requirements-simple.txt not found")
        return False
    
    with open('requirements-simple.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'Flask',
        'Flask-SQLAlchemy',
        'python-dotenv',
        'psycopg2-binary'
    ]
    
    missing_packages = []
    for package in required_packages:
        if package.lower() not in content.lower():
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    print("✅ All required packages found in requirements-simple.txt")
    return True

def check_vercel_config():
    """Check Vercel configuration"""
    print("\n🔍 Checking Vercel configuration...")
    
    if not os.path.exists('vercel.json'):
        print("❌ vercel.json not found")
        return False
    
    try:
        import json
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['version', 'builds', 'routes']
        missing_keys = []
        
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing keys in vercel.json: {', '.join(missing_keys)}")
            return False
        
        print("✅ Vercel configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def check_app_import():
    """Check if the app can be imported"""
    print("\n🔍 Checking app import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Try to import the app
        from app_vercel import app
        print("✅ App imports successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error importing app: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Vercel Deployment Validation")
    print("=" * 40)
    
    checks = [
        check_files,
        check_requirements,
        check_vercel_config,
        check_app_import
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Your project is ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Set up a PostgreSQL database (Supabase, Neon, etc.)")
        print("2. Add environment variables in Vercel dashboard:")
        print("   - DATABASE_URL")
        print("   - SECRET_KEY")
        print("3. Deploy using: vercel")
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 