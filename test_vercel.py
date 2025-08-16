#!/usr/bin/env python3
"""
Test script for Vercel deployment
This script tests the basic functionality of the Flask app
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_vercel_deployment(base_url):
    """Test the Vercel deployment"""
    print(f"Testing Vercel deployment at: {base_url}")
    print("=" * 50)
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "expected_status": 200,
            "description": "Database connectivity test"
        },
        {
            "name": "Simple Test",
            "url": f"{base_url}/test",
            "expected_status": 200,
            "description": "Basic Flask app test"
        },
        {
            "name": "Login Page",
            "url": f"{base_url}/login",
            "expected_status": 200,
            "description": "Login page accessibility"
        },
        {
            "name": "Root Redirect",
            "url": f"{base_url}/",
            "expected_status": 302,  # Redirect to login
            "description": "Root path redirects to login"
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"Testing: {test['name']}")
            print(f"URL: {test['url']}")
            print(f"Expected: {test['expected_status']}")
            
            response = requests.get(test['url'], timeout=10)
            
            print(f"Actual: {response.status_code}")
            
            if response.status_code == test['expected_status']:
                print("✅ PASS")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)}")
                    except:
                        print("Response: HTML content")
            else:
                print("❌ FAIL")
                print(f"Expected {test['expected_status']}, got {response.status_code}")
            
            results.append({
                "test": test['name'],
                "status": "PASS" if response.status_code == test['expected_status'] else "FAIL",
                "expected": test['expected_status'],
                "actual": response.status_code,
                "url": test['url']
            })
            
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test": test['name'],
                "status": "ERROR",
                "error": str(e),
                "url": test['url']
            })
        
        print("-" * 30)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Vercel deployment is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the deployment logs.")
    
    return results

if __name__ == "__main__":
    # Get the base URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter your Vercel app URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not base_url:
        print("No URL provided. Exiting.")
        sys.exit(1)
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    # Run tests
    test_vercel_deployment(base_url) 