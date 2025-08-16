import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'

from app_simple import app

# This is the entry point for Vercel
if __name__ == '__main__':
    app.run() 