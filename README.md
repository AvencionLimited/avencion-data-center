# Avencion Data Center

A Flask-based web application for managing database projects and cohorts.

## Features

- **Project Management**: Create and manage data projects
- **Cohort Management**: Organize data into cohorts within projects
- **Database Integration**: Support for PostgreSQL and SQLite databases
- **Authentication**: Secure login system
- **File Upload**: Support for Excel and Access database files
- **Web Interface**: Modern, responsive web interface

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Databases
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app_simple_working.py
   ```

5. **Access the application**
   - Open http://localhost:5000
   - Login with: Username: `Avencion`, Password: `AvencionData@Center2025`

## Vercel Deployment

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Database**: Set up a PostgreSQL database (recommended options below)

### Database Setup

#### Option 1: Vercel PostgreSQL (Recommended)
1. Go to your Vercel dashboard
2. Create a new PostgreSQL database
3. Copy the connection string
4. Add it as an environment variable: `DATABASE_URL`

#### Option 2: External PostgreSQL Services
- [Supabase](https://supabase.com) - Free tier available
- [Neon](https://neon.tech) - Free tier available
- [Railway](https://railway.app) - Free tier available
- [Heroku Postgres](https://heroku.com/postgres)

### Deployment Steps

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy the application**
   ```bash
   vercel
   ```

4. **Set environment variables in Vercel dashboard**
   - `SECRET_KEY`: A random secret key for Flask sessions
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `FLASK_ENV`: Set to "production"
   - `FLASK_DEBUG`: Set to "0"

5. **Redeploy with environment variables**
   ```bash
   vercel --prod
   ```

### Automated Deployment

Use the provided deployment helper script:

```bash
python deploy-vercel.py
```

This script will:
- Check prerequisites
- Validate your setup
- Guide you through deployment
- Test the deployment

### Testing Your Deployment

Use the test script to verify everything works:

```bash
python test_vercel.py
```

Or manually test these endpoints:
- Health check: `https://your-app.vercel.app/health`
- Database test: `https://your-app.vercel.app/test-db`
- Main app: `https://your-app.vercel.app/`

## Environment Variables

### Required
- `SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URL`: PostgreSQL connection string

### Optional
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (0/1)
- `MAX_CONTENT_LENGTH`: Maximum file upload size
- `PERMANENT_SESSION_LIFETIME`: Session timeout in seconds

## Database Configuration

The application automatically handles database connections:

- **PostgreSQL**: If `DATABASE_URL` contains `postgresql://`
- **SQLite**: Fallback for development (not recommended for production)

### Connection String Format
```
postgresql://username:password@host:port/database
```

## File Structure

```
/
├── api/
│   └── index.py              # Vercel entry point
├── templates/                # Flask templates
├── static/                   # Static files
├── uploads/                  # File uploads (local only)
├── app_simple_working.py     # Main Flask application
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── deploy-vercel.py         # Deployment helper script
├── test_vercel.py           # Test script
└── README.md                # This file
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify your `DATABASE_URL` format
   - Ensure database is accessible from Vercel
   - Check database credentials

2. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check that `api/index.py` can import your app

3. **Timeout Errors**
   - Database operations might be slow on first connection
   - Consider connection pooling for production

4. **File Upload Issues**
   - Vercel has limitations on file uploads
   - Consider external storage (AWS S3, Cloudinary)

### Debug Commands

```bash
# View deployment logs
vercel logs

# Test locally
vercel dev

# Check environment variables
vercel env ls

# Redeploy
vercel --prod
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **Database Security**: Use strong passwords and restrict access
3. **HTTPS**: Vercel automatically provides HTTPS
4. **Rate Limiting**: Consider implementing rate limiting

## Support

If you encounter issues:

1. Check the Vercel deployment logs
2. Test your app locally with `vercel dev`
3. Verify your environment variables
4. Check the `/health` and `/test-db` endpoints
5. Review the `VERCEL_DEPLOYMENT.md` file for detailed troubleshooting

## License

This project is proprietary to Avencion.

## Contributing

For internal development and contributions, please follow the established coding standards and testing procedures. 
