import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'

try:
    from app_vercel_simple import app
    print("✅ Successfully imported app_vercel_simple")
except Exception as e:
    print(f"⚠️ Error importing app_vercel_simple: {e}")
    # Fallback: try to import the main app
    try:
        from app_vercel import app
        print("✅ Successfully imported app_vercel as fallback")
    except Exception as e2:
        print(f"❌ Error importing app_vercel: {e2}")
        raise e2

# This is the entry point for Vercel
# Vercel expects the app to be available as a global variable
app.debug = False

# For Vercel serverless functions
if __name__ == '__main__':
    app.run() 