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
    """Get database URL with proper fallback"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        if 'postgresql://' in DATABASE_URL:
            # Check if we can use PostgreSQL
            try:
                import psycopg2
                print("✅ Using PostgreSQL database from environment")
                return DATABASE_URL
            except ImportError:
                print("⚠️ PostgreSQL URL provided but psycopg2 not available, using SQLite file")
                return 'sqlite:///db_manager.db'
        else:
            print("✅ Using database URL from environment")
            return DATABASE_URL
    else:
        # Fallback to SQLite file for local development
        print("✅ Using SQLite file database for local development")
        return 'sqlite:///db_manager.db'

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

# Configure for larger payloads (for Vercel)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max payload size

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

# Database initialization function
def init_database_tables():
    """Initialize database tables when needed"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            return True
    except Exception as e:
        print(f"⚠️ Database table creation error: {e}")
        print("🔄 Continuing without database tables")
        return False

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
            # Initialize database tables if needed
            init_database_tables()
            
            # Use eager loading to prevent lazy loading issues
            projects = Project.query.options(db.joinedload(Project.cohorts)).order_by(Project.created_at.desc()).all()
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
                # Initialize database tables if needed
                init_database_tables()
                
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
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # Use eager loading to prevent lazy loading issues
            project = Project.query.options(db.joinedload(Project.cohorts)).get_or_404(project_id)
        return render_template('project_detail.html', project=project)
    except Exception as e:
        app.logger.error(f'Project detail error: {e}')
        return jsonify({'error': 'Project detail error', 'details': str(e)}), 500

@app.route('/cohort/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_cohort(project_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # Use eager loading to prevent lazy loading issues
            project = Project.query.options(db.joinedload(Project.cohorts)).get_or_404(project_id)
        
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
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # Use eager loading to prevent lazy loading issues
            cohort = Cohort.query.options(db.joinedload(Cohort.project)).get_or_404(cohort_id)
        return render_template('cohort_detail.html', cohort=cohort)
    except Exception as e:
        app.logger.error(f'Cohort detail error: {e}')
        return jsonify({'error': 'Cohort detail error', 'details': str(e)}), 500

# Edit routes
@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            project = Project.query.get_or_404(project_id)
            
            if request.method == 'POST':
                project.name = request.form['name']
                project.project_type = request.form['project_type']
                project.description = request.form.get('description', '')
                
                db.session.commit()
                flash('Project updated successfully!', 'success')
                return redirect(url_for('project_detail', project_id=project.id))
            
        return render_template('edit_project.html', project=project)
    except Exception as e:
        app.logger.error(f'Edit project error: {e}')
        return jsonify({'error': 'Edit project error', 'details': str(e)}), 500

@app.route('/cohort/<int:cohort_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cohort(cohort_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            cohort = Cohort.query.get_or_404(cohort_id)
            
            if request.method == 'POST':
                cohort.name = request.form['name']
                cohort.description = request.form.get('description', '')
                
                db.session.commit()
                flash('Cohort updated successfully!', 'success')
                return redirect(url_for('cohort_detail', cohort_id=cohort.id))
            
        return render_template('edit_cohort.html', cohort=cohort)
    except Exception as e:
        app.logger.error(f'Edit cohort error: {e}')
        return jsonify({'error': 'Edit cohort error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_spreadsheet(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to detail page
            flash('Edit functionality not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Edit spreadsheet error: {e}')
        return jsonify({'error': 'Edit spreadsheet error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>/edit-online')
@login_required
def edit_spreadsheet_online(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to detail page
            flash('Online editing not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Edit spreadsheet online error: {e}')
        return jsonify({'error': 'Edit spreadsheet online error', 'details': str(e)}), 500

# Database routes (simplified for Vercel)
@app.route('/database/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_database(project_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            project = Project.query.get_or_404(project_id)
        
        if request.method == 'POST':
            flash('Database creation not available in simplified version', 'info')
            return redirect(url_for('project_detail', project_id=project_id))
        
        return render_template('new_database.html', project=project)
    except Exception as e:
        app.logger.error(f'New database error: {e}')
        return jsonify({'error': 'New database error', 'details': str(e)}), 500

@app.route('/database/<int:database_id>/tables')
@login_required
def database_tables(database_id):
    try:
        # For simplified version, return empty tables list
        return jsonify({'tables': []})
    except Exception as e:
        app.logger.error(f'Database tables error: {e}')
        return jsonify({'error': 'Database tables error', 'details': str(e)}), 500

@app.route('/database/<int:database_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_database(database_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to project detail
            flash('Database editing not available in simplified version', 'info')
            return redirect(url_for('project_detail', project_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Edit database error: {e}')
        return jsonify({'error': 'Edit database error', 'details': str(e)}), 500

# Spreadsheet routes (simplified for Vercel)
@app.route('/spreadsheet/create/<int:cohort_id>', methods=['GET', 'POST'])
@login_required
def create_spreadsheet(cohort_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('Spreadsheet creation not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=cohort_id))
    except Exception as e:
        app.logger.error(f'Create spreadsheet error: {e}')
        return jsonify({'error': 'Create spreadsheet error', 'details': str(e)}), 500

@app.route('/spreadsheet/upload/<int:cohort_id>', methods=['GET', 'POST'])
@login_required
def upload_spreadsheet(cohort_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('File upload not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=cohort_id))
    except Exception as e:
        app.logger.error(f'Upload spreadsheet error: {e}')
        return jsonify({'error': 'Upload spreadsheet error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>')
@login_required
def spreadsheet_detail(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('Spreadsheet details not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Spreadsheet detail error: {e}')
        return jsonify({'error': 'Spreadsheet detail error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>/view')
@login_required
def view_spreadsheet(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('Spreadsheet viewing not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'View spreadsheet error: {e}')
        return jsonify({'error': 'View spreadsheet error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>/download')
@login_required
def download_spreadsheet(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('File download not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Download spreadsheet error: {e}')
        return jsonify({'error': 'Download spreadsheet error', 'details': str(e)}), 500

@app.route('/spreadsheet/<int:spreadsheet_id>/recreate', methods=['POST'])
@login_required
def recreate_spreadsheet(spreadsheet_id):
    try:
        with app.app_context():
            # Ensure tables exist before querying
            try:
                db.create_all()
            except:
                pass
            
            # For simplified version, just redirect to cohort detail
            flash('Spreadsheet recreation not available in simplified version', 'info')
            return redirect(url_for('cohort_detail', cohort_id=1))  # Fallback
    except Exception as e:
        app.logger.error(f'Recreate spreadsheet error: {e}')
        return jsonify({'error': 'Recreate spreadsheet error', 'details': str(e)}), 500

@app.route('/help')
@login_required
def help_page():
    try:
        return render_template('help.html')
    except Exception as e:
        app.logger.error(f'Help error: {e}')
        return jsonify({'error': 'Help error', 'details': str(e)}), 500

# Database initialization route
@app.route('/init-db')
def init_database():
    try:
        with app.app_context():
            db.create_all()
            return jsonify({
                'status': 'success',
                'message': 'Database tables created successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        app.logger.error(f'Database initialization error: {e}')
        return jsonify({
            'status': 'error',
            'message': 'Failed to create database tables',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Database connection test route
@app.route('/test-db')
def test_database():
    try:
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Try to query projects
            project_count = Project.query.count()
            
            return jsonify({
                'status': 'success',
                'message': 'Database connection successful',
                'database_url': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI'],
                'tables': tables,
                'project_count': project_count,
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        app.logger.error(f'Database test error: {e}')
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed',
            'error': str(e),
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI'],
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Health check for Vercel
@app.route('/health')
def health_check():
    try:
        # Test database connection and ensure tables exist
        with app.app_context():
            # Try to create tables if they don't exist
            try:
                db.create_all()
            except:
                pass
            
            # Test a simple query
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

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
@app.route('/favicon.png')
def favicon():
    return '', 204  # No content response

# For Vercel deployment
app.debug = False

if __name__ == '__main__':
    # Ensure tables are created for local development
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created for local development")
        except Exception as e:
            print(f"⚠️ Local database initialization error: {e}")
            print("🔄 Continuing without database initialization")
    app.run(debug=True, host='0.0.0.0', port=5000) 