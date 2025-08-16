# Vercel Deployment Guide

## Issue Resolution

The main issue was that Flask-SQLAlchemy was trying to create an instance directory in Vercel's read-only file system. This has been fixed by:

1. **Using in-memory SQLite**: The app now uses `sqlite:///:memory:` for Vercel deployments
2. **Proper Flask configuration**: Added `SQLALCHEMY_ENGINE_OPTIONS` to prevent file system access
3. **Error handling**: Added fallback configurations for SQLAlchemy initialization
4. **Simplified app**: Created `app_vercel_simple.py` specifically for Vercel

## Files Updated

- ✅ `app_vercel_simple.py` - New simplified version for Vercel
- ✅ `api/index.py` - Updated to use the simplified app
- ✅ `requirements.txt` - Added PostgreSQL support
- ✅ `requirements-vercel.txt` - Minimal requirements for Vercel
- ✅ `vercel.json` - Proper configuration

## Deployment Steps

1. **Push your changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment issues"
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
- `DATABASE_URL` - (Optional) PostgreSQL connection string
- `VERCEL` - Set to "1" (automatically set by Vercel)

## Database Configuration

- **Local development**: Uses SQLite file database
- **Vercel deployment**: Uses in-memory SQLite (data is not persistent)
- **Production**: Use PostgreSQL with `DATABASE_URL` environment variable

## Troubleshooting

If you still get errors:

1. **Check the logs**: Look at Vercel function logs for specific errors
2. **Test health endpoint**: Visit `/health` to check database connection
3. **Test simple endpoint**: Visit `/test` to verify Flask is running
4. **Check requirements**: Ensure all dependencies are in `requirements.txt`

## Notes

- The in-memory SQLite database means data will be lost when the function restarts
- For production use, set up a PostgreSQL database (Supabase, Neon, Railway, etc.)
- File uploads are not supported on Vercel (read-only file system)
- Sessions may not persist between function invocations

## Success Indicators

✅ App loads without 500 errors  
✅ `/health` endpoint returns `{"status": "healthy"}`  
✅ `/test` endpoint returns `{"status": "ok"}`  
✅ Login page loads correctly  
✅ Database operations work (with in-memory SQLite)  

Your Avencion Data Center should now deploy successfully on Vercel! 🚀 