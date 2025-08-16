# Vercel Deployment Guide

This guide will help you deploy your Flask application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **PostgreSQL Database**: You'll need a PostgreSQL database (recommended: Supabase, Neon, or Railway)

## Step 1: Set Up Database

### Option A: Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to Settings > Database to get your connection string
4. Copy the connection string (it looks like: `postgresql://postgres:[password]@[host]:5432/postgres`)

### Option B: Neon
1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string from the dashboard

## Step 2: Deploy to Vercel

### Method 1: Using Vercel CLI
1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy from your project directory:
   ```bash
   vercel
   ```

### Method 2: Using Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project settings

## Step 3: Environment Variables

In your Vercel project settings, add these environment variables:

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=0
```

## Step 4: Configure Build Settings

Vercel should automatically detect this as a Python project. The configuration is already set up in:
- `vercel.json` - Project configuration
- `api/index.py` - Entry point
- `app_vercel.py` - Vercel-compatible Flask app

## Step 5: Deploy

1. Push your changes to GitHub
2. Vercel will automatically deploy your application
3. Your app will be available at `https://your-project-name.vercel.app`

## Important Notes

### File System Limitations
- Vercel has a read-only file system
- File uploads are not supported in this version
- The app focuses on project and cohort management

### Database Setup
- The app will automatically create tables on first run
- Make sure your database is accessible from Vercel's servers

### Authentication
- Default login: `Avencion` / `AvencionData@Center2025`
- You can change these credentials in the code

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your `DATABASE_URL` environment variable
   - Ensure your database allows external connections
   - Verify the database credentials

2. **Build Failures**
   - Check the build logs in Vercel dashboard
   - Ensure all dependencies are in `requirements-simple.txt`

3. **Runtime Errors**
   - Check the function logs in Vercel dashboard
   - Verify environment variables are set correctly

### Getting Help

If you encounter issues:
1. Check the Vercel deployment logs
2. Verify your environment variables
3. Test locally with the same database connection

## Local Development

To test locally with the same configuration:

1. Create a `.env` file:
   ```
   DATABASE_URL=your-postgresql-connection-string
   SECRET_KEY=your-secret-key
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-simple.txt
   ```

3. Run the app:
   ```bash
   python app_vercel.py
   ```

## Features Available on Vercel

✅ Project Management
✅ Cohort Management  
✅ User Authentication
✅ Database Integration
✅ Health Check Endpoint

❌ File Uploads (not supported on Vercel)
❌ Excel File Processing (requires file system access)

## Next Steps

After successful deployment:
1. Test the login functionality
2. Create a test project
3. Add cohorts to your project
4. Verify database connectivity

Your Flask application is now deployed and ready to use! 