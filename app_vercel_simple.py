from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import json
import warnings
import hashlib
import secrets
from collections import defaultdict
from dotenv import load_dotenv
import traceback
warnings.filterwarnings('ignore', category=FutureWarning)

# Load environment variables from .env file
load_dotenv()

# Rate limiting for login attempts
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Authentication configuration
AVENCION_USERNAME = "Avencion"
AVENCION_PASSWORD_HASH = hashlib.sha256("AvencionData@Center2025".encode()).hexdigest()

def login_required(f):
    """Decorator to require authentication for routes"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        
        # Additional session validation
        if not session.get('session_id') or not session.get('username'):
            session.clear()
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize database configuration
def get_database_url():
    """Get database URL with fallback to in-memory SQLite"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and 'postgresql://' in DATABASE_URL:
        # Check if psycopg2 is available
        try:
            import psycopg2
            print("✅ Configured for PostgreSQL database on Vercel")
            return DATABASE_URL
        except ImportError:
            print("⚠️ PostgreSQL URL provided but psycopg2 not available, falling back to in-memory SQLite")
            return 'sqlite:///:memory:'
    else:
        print("✅ Using in-memory SQLite database for Vercel")
        return 'sqlite:///:memory:'

# Create Flask app with proper configuration for Vercel
app = Flask(__name__)

# Configure Flask for Vercel's read-only file system
if os.environ.get('VERCEL'):
    # Disable instance path creation for SQLAlchemy
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    print("✅ Configured for Vercel's read-only file system")

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session expires in 24 hours

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

# Set database URL
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with proper error handling for Vercel
try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy initialized successfully")
except Exception as e:
    print(f"⚠️ SQLAlchemy initialization error: {e}")
    # Fallback: try to initialize without instance path
    if os.environ.get('VERCEL'):
        app.config['INSTANCE_PATH'] = None
        db = SQLAlchemy(app)
        print("✅ SQLAlchemy initialized with fallback configuration")
    else:
        raise e

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50), nullable=False, default='other')
    created_by = db.Column(db.String(100), nullable=False, default='Avencion')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cohorts = db.relationship('Cohort', backref='project', lazy=True, cascade='all, delete-orphan')

class Cohort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(100), nullable=False, default='Avencion')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Error handler for debugging
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    app.logger.error(f'Traceback: {traceback.format_exc()}')
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled Exception: {e}')
    app.logger.error(f'Traceback: {traceback.format_exc()}')
    return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Rate limiting check
            client_ip = request.remote_addr
            current_time = datetime.utcnow()
            
            # Clean old attempts
            login_attempts[client_ip] = [attempt for attempt in login_attempts[client_ip] 
                                       if current_time - attempt < timedelta(seconds=LOGIN_TIMEOUT)]
            
            # Check if too many attempts
            if len(login_attempts[client_ip]) >= MAX_LOGIN_ATTEMPTS:
                flash('Too many login attempts. Please try again later.', 'error')
                return render_template('login.html')
            
            # Verify credentials
            if username == AVENCION_USERNAME and hashlib.sha256(password.encode()).hexdigest() == AVENCION_PASSWORD_HASH:
                # Clear login attempts on successful login
                login_attempts[client_ip].clear()
                
                session.permanent = True
                session['authenticated'] = True
                session['username'] = username
                session['login_time'] = current_time.isoformat()
                session['session_id'] = secrets.token_hex(16)
                session['ip_address'] = client_ip
                
                flash('Welcome to Avencion Data Center!', 'success')
                return redirect(url_for('index'))
            else:
                # Record failed attempt
                login_attempts[client_ip].append(current_time)
                flash('Invalid credentials. Please try again.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        app.logger.error(f'Login error: {e}')
        return jsonify({'error': 'Login error', 'details': str(e)}), 500

@app.route('/logout')
def logout():
    try:
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f'Logout error: {e}')
        return jsonify({'error': 'Logout error', 'details': str(e)}), 500

# Main routes
@app.route('/')
@login_required
def index():
    try:
        with app.app_context():
            projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('index.html', projects=projects)
    except Exception as e:
        app.logger.error(f'Index error: {e}')
        return jsonify({'error': 'Index error', 'details': str(e)}), 500

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    try:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            project_type = request.form['project_type']
            created_by = request.form.get('created_by', 'Avencion')
            
            with app.app_context():
                project = Project(name=name, description=description, project_type=project_type, created_by=created_by)
                db.session.add(project)
                db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('index'))
        
        return render_template('new_project.html')
    except Exception as e:
        app.logger.error(f'New project error: {e}')
        return jsonify({'error': 'New project error', 'details': str(e)}), 500

@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    try:
        with app.app_context():
            project = Project.query.get_or_404(project_id)
        return render_template('project_detail.html', project=project)
    except Exception as e:
        app.logger.error(f'Project detail error: {e}')
        return jsonify({'error': 'Project detail error', 'details': str(e)}), 500

@app.route('/cohort/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_cohort(project_id):
    try:
        with app.app_context():
            project = Project.query.get_or_404(project_id)
        
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            created_by = request.form.get('created_by', 'Avencion')
            
            with app.app_context():
                cohort = Cohort(name=name, description=description, project_id=project_id, created_by=created_by)
                db.session.add(cohort)
                db.session.commit()
            
            flash('Cohort created successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))
        
        return render_template('new_cohort.html', project=project)
    except Exception as e:
        app.logger.error(f'New cohort error: {e}')
        return jsonify({'error': 'New cohort error', 'details': str(e)}), 500

@app.route('/cohort/<int:cohort_id>')
@login_required
def cohort_detail(cohort_id):
    try:
        with app.app_context():
            cohort = Cohort.query.get_or_404(cohort_id)
        return render_template('cohort_detail.html', cohort=cohort)
    except Exception as e:
        app.logger.error(f'Cohort detail error: {e}')
        return jsonify({'error': 'Cohort detail error', 'details': str(e)}), 500

@app.route('/help')
@login_required
def help_page():
    try:
        return render_template('help.html')
    except Exception as e:
        app.logger.error(f'Help error: {e}')
        return jsonify({'error': 'Help error', 'details': str(e)}), 500

# Health check for Vercel
@app.route('/health')
def health_check():
    try:
        # Test database connection
        with app.app_context():
            db.engine.execute('SELECT 1')
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        app.logger.error(f'Health check error: {e}')
        return jsonify({
            'status': 'unhealthy', 
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# Simple test route without database
@app.route('/test')
def test():
    return jsonify({
        'status': 'ok',
        'message': 'Flask app is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# For Vercel deployment
app.debug = False

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")
            print("🔄 Continuing without database initialization")
    app.run(debug=True, host='0.0.0.0', port=5000) 