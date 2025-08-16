# VPS Deployment Guide

## PostgreSQL Server Setup

### 1. Check PostgreSQL Server Status

First, verify your PostgreSQL server is running and accessible:

```bash
# Test connection from your local machine
psql -h 199.188.204.28 -p 5432 -U datacenter_user -d datacenter_db
```

### 2. PostgreSQL Configuration Issues

If connection fails, check these common issues:

#### A. PostgreSQL Service Status
```bash
# On your VPS, check if PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl start postgresql
```

#### B. PostgreSQL Configuration Files
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf

# Ensure these lines are set:
listen_addresses = '*'
port = 5432
```

#### C. Client Authentication
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Add this line to allow connections:
host    all             all             0.0.0.0/0               md5
```

#### D. Firewall Settings
```bash
# Allow PostgreSQL port
sudo ufw allow 5432
sudo ufw status
```

### 3. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

## Application Deployment

### Option 1: Direct Deployment

1. **Upload files to VPS**
```bash
# On your VPS
mkdir -p /opt/database-manager
cd /opt/database-manager
```

2. **Install Python and dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://datacenter_user:DataCenter2025**Secure@199.188.204.28:5432/datacenter_db
```

4. **Run the application**
```bash
python app-simple.py
```

### Option 2: Docker Deployment (Recommended)

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p uploads

EXPOSE 5000
CMD ["python", "app-simple.py"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://datacenter_user:DataCenter2025**Secure@199.188.204.28:5432/datacenter_db
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

3. **Deploy with Docker**
```bash
docker-compose up -d
```

### Option 3: Using Gunicorn (Production)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Create WSGI file**
```python
# wsgi.py
from app_simple import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Troubleshooting

### Connection Issues

1. **Test PostgreSQL connection**
```bash
psql -h 199.188.204.28 -p 5432 -U datacenter_user -d datacenter_db
```

2. **Check network connectivity**
```bash
telnet 199.188.204.28 5432
```

3. **Verify credentials**
```bash
# Test with psql
psql "postgresql://datacenter_user:DataCenter2025**Secure@199.188.204.28:5432/datacenter_db"
```

### Application Issues

1. **Check logs**
```bash
# If using Docker
docker-compose logs

# If running directly
python app-simple.py
```

2. **Database migration**
```bash
# The app will automatically migrate, but you can check manually
python -c "from app_simple import app, db; app.app_context().push(); db.create_all()"
```

## Security Considerations

1. **Use environment variables for sensitive data**
```bash
export DATABASE_URL=postgresql://user:password@host:port/db
export SECRET_KEY=your-secret-key
```

2. **Set up SSL/TLS for PostgreSQL**
3. **Configure firewall rules**
4. **Use strong passwords**
5. **Regular backups**

## Monitoring

1. **Check application status**
```bash
curl http://localhost:5000
```

2. **Monitor database connections**
```bash
psql -h 199.188.204.28 -U datacenter_user -d datacenter_db -c "SELECT * FROM pg_stat_activity;"
```

3. **Check disk space**
```bash
df -h
du -sh uploads/
```

## Backup Strategy

1. **Database backup**
```bash
pg_dump -h 199.188.204.28 -U datacenter_user datacenter_db > backup.sql
```

2. **Upload files backup**
```bash
tar -czf uploads_backup.tar.gz uploads/
```

## Next Steps

1. **Set up reverse proxy (nginx)**
2. **Configure SSL certificates**
3. **Set up monitoring and logging**
4. **Implement automated backups**
5. **Set up CI/CD pipeline** 