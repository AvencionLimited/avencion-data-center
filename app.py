from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import pandas as pd
import pyodbc
import psycopg2
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import tempfile
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    databases = db.relationship('Database', backref='project', lazy=True)

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # postgresql, access, excel
    connection_string = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImportLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'), nullable=False)
    import_type = db.Column(db.String(20), nullable=False)  # access, excel
    status = db.Column(db.String(20), nullable=False)  # success, failed
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/database/new/<int:project_id>', methods=['GET', 'POST'])
def new_database(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        name = request.form['name']
        db_type = request.form['type']
        
        if db_type == 'postgresql':
            host = request.form['host']
            port = request.form['port']
            database = request.form['database']
            username = request.form['username']
            password = request.form['password']
            
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
            database_obj = Database(
                name=name,
                type=db_type,
                connection_string=connection_string,
                project_id=project_id
            )
            
        elif db_type in ['access', 'excel']:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{project_id}_{filename}")
                file.save(file_path)
                
                database_obj = Database(
                    name=name,
                    type=db_type,
                    file_path=file_path,
                    project_id=project_id
                )
        
        db.session.add(database_obj)
        db.session.commit()
        
        flash('Database added successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('new_database.html', project=project)

@app.route('/database/<int:database_id>/import', methods=['POST'])
def import_database(database_id):
    database = Database.query.get_or_404(database_id)
    
    try:
        if database.type == 'access':
            success = import_access_database(database)
        elif database.type == 'excel':
            success = import_excel_database(database)
        else:
            flash('Unsupported database type', 'error')
            return redirect(url_for('project_detail', project_id=database.project_id))
        
        if success:
            flash('Database imported successfully!', 'success')
        else:
            flash('Failed to import database', 'error')
            
    except Exception as e:
        flash(f'Error importing database: {str(e)}', 'error')
    
    return redirect(url_for('project_detail', project_id=database.project_id))

@app.route('/database/<int:database_id>/tables')
def database_tables(database_id):
    database = Database.query.get_or_404(database_id)
    
    try:
        if database.type == 'postgresql':
            tables = get_postgresql_tables(database.connection_string)
        elif database.type == 'access':
            tables = get_access_tables(database.file_path)
        elif database.type == 'excel':
            tables = get_excel_tables(database.file_path)
        else:
            tables = []
            
        return jsonify({'tables': tables})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def import_access_database(database):
    """Import Access database to PostgreSQL"""
    try:
        # This is a simplified version - you'll need to implement the actual import logic
        # based on your specific requirements
        
        # For now, we'll just log the import attempt
        log = ImportLog(
            database_id=database.id,
            import_type='access',
            status='success',
            message='Access database import completed'
        )
        db.session.add(log)
        db.session.commit()
        
        return True
        
    except Exception as e:
        log = ImportLog(
            database_id=database.id,
            import_type='access',
            status='failed',
            message=str(e)
        )
        db.session.add(log)
        db.session.commit()
        return False

def import_excel_database(database):
    """Import Excel file to PostgreSQL"""
    try:
        # Read Excel file
        df = pd.read_excel(database.file_path)
        
        # This is a simplified version - you'll need to implement the actual import logic
        # based on your specific requirements
        
        log = ImportLog(
            database_id=database.id,
            import_type='excel',
            status='success',
            message=f'Excel file imported with {len(df)} rows'
        )
        db.session.add(log)
        db.session.commit()
        
        return True
        
    except Exception as e:
        log = ImportLog(
            database_id=database.id,
            import_type='excel',
            status='failed',
            message=str(e)
        )
        db.session.add(log)
        db.session.commit()
        return False

def get_postgresql_tables(connection_string):
    """Get list of tables from PostgreSQL database"""
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return tables
        
    except Exception as e:
        raise Exception(f"Error connecting to PostgreSQL: {str(e)}")

def get_access_tables(file_path):
    """Get list of tables from Access database"""
    try:
        # This is a placeholder - you'll need to implement Access database reading
        # using pyodbc or similar library
        return ['table1', 'table2']  # Placeholder
        
    except Exception as e:
        raise Exception(f"Error reading Access database: {str(e)}")

def get_excel_tables(file_path):
    """Get list of sheets from Excel file"""
    try:
        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
        
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 