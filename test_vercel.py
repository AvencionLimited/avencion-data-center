#!/usr/bin/env python3
"""
Test script for Vercel deployment verification
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_local_app():
    """Test the app locally"""
    print("🧪 Testing local app...")
    
    try:
        # Import the app
        sys.path.append('.')
        from app_simple_working import app
        
        # Test database connection
        with app.app_context():
            from app_simple_working import db
            db.create_all()
            print("✅ Database tables created successfully")
        
        # Test basic functionality
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test database endpoint
            response = client.get('/test-db')
            if response.status_code == 200:
                print("✅ Database test endpoint working")
            else:
                print(f"❌ Database test endpoint failed: {response.status_code}")
                return False
            
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ Login page accessible")
            else:
                print(f"❌ Login page failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def test_vercel_deployment(url):
    """Test the deployed app on Vercel"""
    print(f"\n🌐 Testing Vercel deployment at: {url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test database endpoint
        response = requests.get(f"{url}/test-db", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database test: {data.get('status', 'unknown')}")
            if 'project_count' in data:
                print(f"   Projects in database: {data['project_count']}")
        else:
            print(f"❌ Database test failed: {response.status_code}")
            return False
        
        # Test main page (should redirect to login)
        response = requests.get(url, timeout=10)
        if response.status_code in [200, 302]:
            print("✅ Main page accessible")
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment...")
    
    # Check environment variables
    env_vars = {
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'FLASK_ENV': os.environ.get('FLASK_ENV'),
        'VERCEL': os.environ.get('VERCEL')
    }
    
    for var, value in env_vars.items():
        if value:
            if 'password' in var.lower() or 'secret' in var.lower():
                print(f"✅ {var}: {'*' * 10}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set")
    
    # Check if we're in Vercel
    if os.environ.get('VERCEL'):
        print("✅ Running in Vercel environment")
    else:
        print("ℹ️  Running in local environment")

def main():
    """Main test function"""
    print("🧪 Avencion Data Center - Vercel Test Suite")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Test local app
    if not test_local_app():
        print("\n❌ Local tests failed. Fix issues before deploying.")
        return
    
    print("\n✅ All local tests passed!")
    
    # Ask for Vercel URL to test
    print("\n" + "=" * 50)
    url = input("Enter your Vercel deployment URL (or press Enter to skip): ").strip()
    
    if url:
        if not url.startswith('http'):
            url = f"https://{url}"
        
        if test_vercel_deployment(url):
            print("\n🎉 All tests passed! Your deployment is working correctly.")
        else:
            print("\n❌ Some deployment tests failed. Check your Vercel logs.")
    else:
        print("\n📋 To test your deployment:")
        print("1. Deploy to Vercel: vercel --prod")
        print("2. Run this script again with your deployment URL")
        print("3. Check the health endpoints manually")

if __name__ == '__main__':
    main() 