from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import hashlib
import secrets
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Rate limiting for login attempts
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes

# Authentication configuration
AVENCION_USERNAME = "Avencion"
AVENCION_PASSWORD_HASH = hashlib.sha256("AvencionData@Center2025".encode()).hexdigest()

def login_required(f):
    """Decorator to require authentication for routes"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Database configuration - simple and reliable
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and 'postgresql://' in DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("✅ Using PostgreSQL database")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_manager.db'
    print("✅ Using SQLite database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Simple models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50), default='other')
    created_by = db.Column(db.String(100), default='Avencion')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cohorts = db.relationship('Cohort', backref='project', lazy=True, cascade='all, delete-orphan')

class Cohort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(100), default='Avencion')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Simple routes
@app.route('/')
@login_required
def index():
    try:
        with app.app_context():
            db.create_all()
            projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('index.html', projects=projects)
    except Exception as e:
        return jsonify({'error': 'Index error', 'details': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == AVENCION_USERNAME and hashlib.sha256(password.encode()).hexdigest() == AVENCION_PASSWORD_HASH:
            session.permanent = True
            session['authenticated'] = True
            session['username'] = username
            flash('Welcome to Avencion Data Center!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        try:
            with app.app_context():
                db.create_all()
                project = Project(
                    name=request.form['name'],
                    description=request.form['description'],
                    project_type=request.form['project_type'],
                    created_by=request.form.get('created_by', 'Avencion')
                )
                db.session.add(project)
                db.session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            return jsonify({'error': 'New project error', 'details': str(e)}), 500
    
    return render_template('new_project.html')

@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    try:
        with app.app_context():
            db.create_all()
            project = Project.query.get_or_404(project_id)
        return render_template('project_detail.html', project=project)
    except Exception as e:
        return jsonify({'error': 'Project detail error', 'details': str(e)}), 500

@app.route('/cohort/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_cohort(project_id):
    try:
        with app.app_context():
            db.create_all()
            project = Project.query.get_or_404(project_id)
        
        if request.method == 'POST':
            with app.app_context():
                cohort = Cohort(
                    name=request.form['name'],
                    description=request.form['description'],
                    project_id=project_id,
                    created_by=request.form.get('created_by', 'Avencion')
                )
                db.session.add(cohort)
                db.session.commit()
            flash('Cohort created successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))
        
        return render_template('new_cohort.html', project=project)
    except Exception as e:
        return jsonify({'error': 'New cohort error', 'details': str(e)}), 500

@app.route('/cohort/<int:cohort_id>')
@login_required
def cohort_detail(cohort_id):
    try:
        with app.app_context():
            db.create_all()
            cohort = Cohort.query.get_or_404(cohort_id)
        return render_template('cohort_detail.html', cohort=cohort)
    except Exception as e:
        return jsonify({'error': 'Cohort detail error', 'details': str(e)}), 500

# Database routes (simplified)
@app.route('/database/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_database(project_id):
    try:
        with app.app_context():
            db.create_all()
            project = Project.query.get_or_404(project_id)
        if request.method == 'POST':
            flash('Database creation not available in simplified version', 'info')
            return redirect(url_for('project_detail', project_id=project_id))
        return render_template('new_database.html', project=project)
    except Exception as e:
        return jsonify({'error': 'New database error', 'details': str(e)}), 500

@app.route('/database/<int:database_id>/tables')
@login_required
def database_tables(database_id):
    return jsonify({'tables': ['table1', 'table2']})

@app.route('/database/<int:database_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_database(database_id):
    flash('Database editing not available in simplified version', 'info')
    return redirect(url_for('index'))

# Spreadsheet routes (simplified)
@app.route('/spreadsheet/create/<int:cohort_id>', methods=['GET', 'POST'])
@login_required
def create_spreadsheet(cohort_id):
    flash('Spreadsheet creation not available in simplified version', 'info')
    return redirect(url_for('cohort_detail', cohort_id=cohort_id))

@app.route('/spreadsheet/upload/<int:cohort_id>', methods=['GET', 'POST'])
@login_required
def upload_spreadsheet(cohort_id):
    flash('File upload not available in simplified version', 'info')
    return redirect(url_for('cohort_detail', cohort_id=cohort_id))

@app.route('/spreadsheet/<int:spreadsheet_id>')
@login_required
def spreadsheet_detail(spreadsheet_id):
    flash('Spreadsheet details not available in simplified version', 'info')
    return redirect(url_for('index'))

@app.route('/spreadsheet/<int:spreadsheet_id>/view')
@login_required
def view_spreadsheet(spreadsheet_id):
    flash('Spreadsheet viewing not available in simplified version', 'info')
    return redirect(url_for('index'))

@app.route('/spreadsheet/<int:spreadsheet_id>/download')
@login_required
def download_spreadsheet(spreadsheet_id):
    flash('File download not available in simplified version', 'info')
    return redirect(url_for('index'))

@app.route('/spreadsheet/<int:spreadsheet_id>/recreate', methods=['POST'])
@login_required
def recreate_spreadsheet(spreadsheet_id):
    flash('Spreadsheet recreation not available in simplified version', 'info')
    return redirect(url_for('index'))

# Edit routes (simplified)
@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    try:
        with app.app_context():
            db.create_all()
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
        return jsonify({'error': 'Edit project error', 'details': str(e)}), 500

@app.route('/cohort/<int:cohort_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cohort(cohort_id):
    try:
        with app.app_context():
            db.create_all()
            cohort = Cohort.query.get_or_404(cohort_id)
            if request.method == 'POST':
                cohort.name = request.form['name']
                cohort.description = request.form.get('description', '')
                db.session.commit()
                flash('Cohort updated successfully!', 'success')
                return redirect(url_for('cohort_detail', cohort_id=cohort.id))
        return render_template('edit_cohort.html', cohort=cohort)
    except Exception as e:
        return jsonify({'error': 'Edit cohort error', 'details': str(e)}), 500

# Test routes
@app.route('/test')
def test():
    return jsonify({
        'status': 'ok',
        'message': 'Flask app is running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/test-db')
def test_database():
    try:
        with app.app_context():
            db.create_all()
            # Use text() for raw SQL in newer SQLAlchemy versions
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            project_count = Project.query.count()
            return jsonify({
                'status': 'success',
                'message': 'Database connection successful',
                'database_url': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI'],
                'project_count': project_count,
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed',
            'error': str(e),
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI'],
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health_check():
    try:
        with app.app_context():
            db.create_all()
            # Use text() for raw SQL in newer SQLAlchemy versions
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy', 
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# Favicon routes
@app.route('/favicon.ico')
@app.route('/favicon.png')
def favicon():
    return '', 204

# Help route
@app.route('/help')
@login_required
def help_page():
    return render_template('help.html')

# For Vercel deployment
app.debug = False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 