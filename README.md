# Database Manager Platform

A web-based platform for managing databases from different projects with support for PostgreSQL, Microsoft Access, and Excel files.

## Features

- **Project Management**: Organize databases into projects with dates
- **PostgreSQL Support**: Connect to and manage PostgreSQL databases
- **Access Database Import**: Import Microsoft Access (.mdb/.accdb) files
- **Excel Import**: Import Excel (.xlsx/.xls) files
- **Modern Web Interface**: Beautiful, responsive UI built with Bootstrap
- **Database Migration**: Import Access and Excel data into PostgreSQL
- **Table Viewer**: View tables and structure from connected databases

## Requirements

- Python 3.8+
- PostgreSQL (for production)
- Microsoft Access Database Engine (for Access file support)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Databases
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///db_manager.db
FLASK_ENV=development
FLASK_DEBUG=1
```

### PostgreSQL Setup (Production)

For production, use PostgreSQL as the main database:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/db_manager
```

## Usage

### Starting the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Creating Projects

1. Navigate to the dashboard
2. Click "New Project"
3. Enter project name and description
4. Click "Create Project"

### Adding Databases

1. Open a project
2. Click "Add Database"
3. Choose database type:
   - **PostgreSQL**: Enter connection details
   - **Access**: Upload .mdb/.accdb file
   - **Excel**: Upload .xlsx/.xls file

### Importing Data

1. For Access or Excel databases, click "Import to PostgreSQL"
2. The system will attempt to import the data into a PostgreSQL database
3. Check the import logs for status

## Project Structure

```
Databases/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── new_project.html
│   ├── project_detail.html
│   └── new_database.html
├── uploads/             # Uploaded files
└── README.md           # This file
```

## Database Models

### Project
- `id`: Primary key
- `name`: Project name
- `description`: Project description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Database
- `id`: Primary key
- `name`: Database name
- `type`: Database type (postgresql, access, excel)
- `connection_string`: PostgreSQL connection string
- `file_path`: Path to uploaded file
- `project_id`: Foreign key to Project
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### ImportLog
- `id`: Primary key
- `database_id`: Foreign key to Database
- `import_type`: Type of import (access, excel)
- `status`: Import status (success, failed)
- `message`: Import message
- `created_at`: Creation timestamp

## Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

- Change the default `SECRET_KEY`
- Use HTTPS in production
- Implement proper authentication
- Validate file uploads
- Use environment variables for sensitive data

## Troubleshooting

### Access Database Issues

- Ensure Microsoft Access Database Engine is installed
- Check file permissions
- Verify .mdb/.accdb file format

### PostgreSQL Connection Issues

- Verify connection string format
- Check network connectivity
- Ensure PostgreSQL is running
- Verify user permissions

### File Upload Issues

- Check file size limits
- Verify file format
- Ensure upload directory permissions

## CREDENTIALS

- USERNAME: Avencion
- PASSWORD: AvencionData@Center2025

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 
