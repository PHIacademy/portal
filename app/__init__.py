from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError(
            'DATABASE_URL environment variable is not set. '
            'Please configure it in your Vercel project settings.'
        )
    
    # Handle special case where Vercel might modify the DATABASE_URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300,
    }
    
    # Initialize plugins
    db.init_app(app)
    
    with app.app_context():
        # Import routes
        from app.routes import main, subject, article, auth
        
        # Register blueprints
        app.register_blueprint(main.bp)
        app.register_blueprint(subject.bp)
        app.register_blueprint(article.bp)
        app.register_blueprint(auth.auth)
        
        # Create database tables
        db.create_all()
        
        # Initialize default subjects if none exist
        from app.models import Subject
        if not Subject.query.first():
            default_subjects = [
                Subject(name='Chinese', description='Chinese language and literature'),
                Subject(name='English', description='English language and literature'),
                Subject(name='Math', description='Mathematics and problem solving')
            ]
            for subject in default_subjects:
                db.session.add(subject)
            db.session.commit()
            
    return app
