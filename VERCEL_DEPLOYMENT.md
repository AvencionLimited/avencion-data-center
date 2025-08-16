# Vercel Deployment Guide for Avencion Data Center

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Database Setup

### Option 1: PostgreSQL on Vercel (Recommended)
1. Go to your Vercel dashboard
2. Create a new PostgreSQL database
3. Copy the connection string
4. Add it as an environment variable: `DATABASE_URL`

### Option 2: External PostgreSQL Database
- Use services like:
  - [Supabase](https://supabase.com) (Free tier available)
  - [Neon](https://neon.tech) (Free tier available)
  - [Railway](https://railway.app) (Free tier available)
  - [Heroku Postgres](https://heroku.com/postgres)

### Option 3: SQLite (Development Only)
- For testing, the app will fall back to SQLite if no PostgreSQL connection is provided

## Environment Variables

Set these in your Vercel project settings:

```bash
# Required
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database

# Optional
FLASK_ENV=production
FLASK_DEBUG=0
```

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from your project directory
```bash
cd /path/to/your/project
vercel
```

### 4. Follow the prompts:
- Set up and deploy? `Y`
- Which scope? `Select your account`
- Link to existing project? `N`
- Project name? `avencion-data-center` (or your preferred name)
- Directory? `./` (current directory)
- Override settings? `N`

### 5. Set Environment Variables
After deployment, go to your Vercel dashboard:
1. Select your project
2. Go to Settings → Environment Variables
3. Add the required environment variables

### 6. Redeploy with Environment Variables
```bash
vercel --prod
```

## File Structure for Vercel

Your project should have this structure:
```
/
├── api/
│   └── index.py          # Vercel entry point
├── templates/            # Flask templates
├── static/              # Static files (if any)
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── app_simple_working.py # Main Flask app
```

## Database Connection

The app automatically handles database connections:
- If `DATABASE_URL` is set and contains `postgresql://`, it uses PostgreSQL
- Otherwise, it falls back to SQLite for development

## Testing Your Deployment

1. **Health Check**: Visit `https://your-app.vercel.app/health`
2. **Database Test**: Visit `https://your-app.vercel.app/test-db`
3. **Main App**: Visit `https://your-app.vercel.app/`

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**
   - Check your `DATABASE_URL` format
   - Ensure your database is accessible from Vercel's servers
   - Verify database credentials

2. **Import Errors**
   - Check that all dependencies are in `requirements.txt`
   - Ensure `api/index.py` can import your main app

3. **Timeout Errors**
   - Database operations might be slow on first connection
   - Consider using connection pooling for production

4. **File Upload Issues**
   - Vercel has limitations on file uploads
   - Consider using external storage (AWS S3, Cloudinary, etc.)

### Debug Commands:

```bash
# View deployment logs
vercel logs

# Test locally
vercel dev

# Check environment variables
vercel env ls
```

## Performance Optimization

1. **Database Connection Pooling**: Consider using connection pooling for better performance
2. **Caching**: Implement caching for frequently accessed data
3. **CDN**: Use Vercel's CDN for static assets
4. **Edge Functions**: Consider using Vercel Edge Functions for better performance

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **Database Security**: Use strong passwords and restrict database access
3. **HTTPS**: Vercel automatically provides HTTPS
4. **Rate Limiting**: Consider implementing rate limiting for your API endpoints

## Support

If you encounter issues:
1. Check the Vercel deployment logs
2. Test your app locally with `vercel dev`
3. Verify your environment variables
4. Check the `/health` and `/test-db` endpoints

## Next Steps

After successful deployment:
1. Set up a custom domain (optional)
2. Configure monitoring and alerts
3. Set up CI/CD for automatic deployments
4. Implement backup strategies for your database 