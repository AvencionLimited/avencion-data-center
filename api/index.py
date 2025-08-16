import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'

try:
    from app_simple_working import app
    print("✅ Successfully imported app_simple_working")
except Exception as e:
    print(f"⚠️ Error importing app_simple_working: {e}")
    # Fallback: try to import the main app
    try:
        from app_vercel import app
        print("✅ Successfully imported app_vercel as fallback")
    except Exception as e2:
        print(f"❌ Error importing app_vercel: {e2}")
        # Final fallback: try the original app
        try:
            from app import app
            print("✅ Successfully imported app as final fallback")
        except Exception as e3:
            print(f"❌ Error importing app: {e3}")
            raise e3

# This is the entry point for Vercel
# Vercel expects the app to be available as a global variable
app.debug = False

# Initialize database tables on startup
try:
    with app.app_context():
        from app_simple_working import db
        db.create_all()
        print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

# For Vercel serverless functions
if __name__ == '__main__':
    app.run() 