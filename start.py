#!/usr/bin/env python3
"""
Database Manager Startup Script
Initializes the database and starts the Flask application
"""

import os
import sys
from app import app, db

def init_database():
    """Initialize the database with tables"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚀 Starting Database Manager...")
    
    # Initialize database
    init_database()
    
    # Get configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print("📊 Database Manager is ready!")
    
    # Start the application
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main() 