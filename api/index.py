import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'

from app_vercel import app

# This is the entry point for Vercel
# Vercel expects the app to be available as a global variable
app.debug = False

# For Vercel serverless functions
if __name__ == '__main__':
    app.run() 