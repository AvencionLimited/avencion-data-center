# Vercel Deployment Guide

## Issue Resolution

The main issues were:
1. **Flask-SQLAlchemy trying to create an instance directory** in Vercel's read-only file system
2. **psycopg2-binary failing to build** due to missing PostgreSQL development libraries

These have been fixed by:

1. **Using in-memory SQLite**: The app now uses `sqlite:///:memory:` for Vercel deployments
2. **Removing PostgreSQL dependencies**: Eliminated `psycopg2-binary` from requirements to avoid build failures
3. **Proper Flask configuration**: Added `SQLALCHEMY_ENGINE_OPTIONS` to prevent file system access
4. **Error handling**: Added fallback configurations for SQLAlchemy initialization
5. **Simplified app**: Created `app_vercel_simple.py` specifically for Vercel

## Files Updated

- ✅ `app_vercel_simple.py` - New simplified version for Vercel
- ✅ `api/index.py` - Updated to use the simplified app
- ✅ `requirements.txt` - Removed problematic dependencies
- ✅ `requirements-vercel.txt` - Minimal requirements for Vercel
- ✅ `vercel.json` - Updated configuration
- ✅ `test_vercel.py` - Test script for deployment verification
- ✅ `VERCEL_DEPLOYMENT.md` - Updated troubleshooting guide

## Deployment Steps

1. **Push your changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix Vercel build: Remove psycopg2 dependency"
   git push
   ```

2. **Redeploy on Vercel**:
   - Go to your Vercel dashboard
   - Select your project
   - Click "Redeploy" or push new changes to trigger auto-deployment

3. **Test the deployment**:
   - Visit your Vercel URL
   - Test the health check: `https://your-app.vercel.app/health`
   - Test the simple route: `https://your-app.vercel.app/test`

## Environment Variables

Make sure you have these environment variables set in Vercel:

- `SECRET_KEY` - A random secret key for Flask sessions
- `VERCEL` - Set to "1" (automatically set by Vercel)

## Database Configuration

- **Vercel deployment**: Uses in-memory SQLite (data is not persistent)
- **Local development**: Can use SQLite file database or PostgreSQL
- **Production**: For persistent data, consider using external database services

## Important Notes

- **Data persistence**: The in-memory SQLite database means data will be lost when the function restarts
- **PostgreSQL support**: Removed from Vercel deployment to avoid build issues
- **File uploads**: Not supported on Vercel (read-only file system)
- **Sessions**: May not persist between function invocations

## Troubleshooting

If you still get errors:

1. **Check the logs**: Look at Vercel function logs for specific errors
2. **Test health endpoint**: Visit `/health` to check database connection
3. **Test simple endpoint**: Visit `/test` to verify Flask is running
4. **Check requirements**: Ensure all dependencies are in `requirements.txt`

## Success Indicators

✅ App loads without 500 errors  
✅ `/health` endpoint returns `{"status": "healthy"}`  
✅ `/test` endpoint returns `{"status": "ok"}`  
✅ Login page loads correctly  
✅ Database operations work (with in-memory SQLite)  

Your Avencion Data Center should now deploy successfully on Vercel! 🚀 