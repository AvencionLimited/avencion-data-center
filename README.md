# Database Manager - Flask Application

A Flask-based web application for managing projects, cohorts, and databases. This application provides a comprehensive interface for data management with authentication and user-friendly features.

## Features

- **Project Management**: Create and manage projects with different types
- **Cohort Management**: Organize data into cohorts within projects
- **User Authentication**: Secure login system with rate limiting
- **Database Integration**: Support for PostgreSQL databases
- **Responsive UI**: Modern interface built with Tailwind CSS

## Quick Deploy to Vercel

### Prerequisites
1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **PostgreSQL Database**: Set up a database (recommended: [Supabase](https://supabase.com) or [Neon](https://neon.tech))

### Deployment Steps

1. **Fork/Clone this repository**

2. **Set up a PostgreSQL database**:
   - Go to [supabase.com](https://supabase.com) and create a free project
   - Copy your database connection string

3. **Deploy to Vercel**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy
   vercel
   ```

4. **Configure Environment Variables** in Vercel dashboard:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   FLASK_DEBUG=0
   ```

5. **Access your app** at `https://your-project-name.vercel.app`

### Default Login Credentials
- **Username**: `Avencion`
- **Password**: `AvencionData@Center2025`

## Local Development

### Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Databases
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-simple.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   SECRET_KEY=your-secret-key-here
   ```

4. **Run the application**:
   ```bash
   python app_vercel.py
   ```

5. **Access the app** at `http://localhost:5000`

## Project Structure

```
Databases/
├── api/
│   └── index.py              # Vercel entry point
├── templates/                # HTML templates
├── app_vercel.py            # Main Flask application (Vercel-compatible)
├── app_simple.py            # Full-featured Flask application
├── requirements-simple.txt   # Python dependencies
├── vercel.json              # Vercel configuration
├── deploy-vercel.py         # Deployment validation script
└── VERCEL_DEPLOYMENT.md     # Detailed deployment guide
```

## Features Available on Vercel

✅ **Project Management**: Create, edit, and delete projects
✅ **Cohort Management**: Organize data into cohorts
✅ **User Authentication**: Secure login with session management
✅ **Database Integration**: PostgreSQL database support
✅ **Health Check**: `/health` endpoint for monitoring

❌ **File Uploads**: Not supported on Vercel (read-only file system)
❌ **Excel Processing**: Requires file system access

## Database Setup

The application automatically creates the necessary database tables on first run. Make sure your PostgreSQL database is accessible and the connection string is correctly configured.

## Security Features

- **Rate Limiting**: Prevents brute force attacks on login
- **Session Management**: Secure session handling with expiration
- **Input Validation**: Sanitized user inputs
- **Security Headers**: XSS protection and other security headers

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify your `DATABASE_URL` environment variable
   - Ensure your database allows external connections
   - Check database credentials

2. **Build Failures**
   - Check Vercel build logs
   - Verify all dependencies are in `requirements-simple.txt`

3. **Runtime Errors**
   - Check Vercel function logs
   - Verify environment variables are set correctly

### Validation

Run the deployment validation script to check your setup:
```bash
python deploy-vercel.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For deployment issues, refer to the [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) file for detailed instructions. 
