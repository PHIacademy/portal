import os
import sys
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Subject, Article, User
from app import db

def create_sqlite_app():
    """Create a Flask app instance with SQLite configuration"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/educational_portal.db'
    db.init_app(app)
    return app

def create_postgres_app():
    """Create a Flask app instance with Postgres configuration"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 300,
    }
    db.init_app(app)
    return app

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    # Create both app instances
    sqlite_app = create_sqlite_app()
    postgres_app = create_postgres_app()

    # Start with SQLite context to read data
    with sqlite_app.app_context():
        try:
            # Get all data from SQLite
            subjects = Subject.query.all()
            articles = Article.query.all()
            users = User.query.all()

            # Store data in memory
            subjects_data = [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'created_at': s.created_at,
                    'is_chinese': s.is_chinese
                } for s in subjects
            ]
            
            articles_data = [
                {
                    'id': a.id,
                    'subject_id': a.subject_id,
                    'title': a.title,
                    'level': a.level,
                    'genre': a.genre,
                    'html_content': a.html_content,
                    'html_path': a.html_path,
                    'uploaded_at': a.uploaded_at
                } for a in articles
            ]
            
            users_data = [
                {
                    'id': u.id,
                    'email': u.email,
                    'username': u.username,
                    'password_hash': u.password_hash,
                    'created_at': u.created_at,
                    'is_active': u.is_active,
                    'last_login': u.last_login,
                    'role': u.role,
                    'auth_provider': u.auth_provider,
                    'auth_provider_id': u.auth_provider_id,
                    'reset_password_token': u.reset_password_token,
                    'reset_password_expires': u.reset_password_expires,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'profile_picture': u.profile_picture,
                    'bio': u.bio
                } for u in users
            ]

            print(f"Read {len(subjects)} subjects, {len(articles)} articles, and {len(users)} users from SQLite")

        except Exception as e:
            print(f"Error reading from SQLite: {str(e)}")
            return False

    # Switch to PostgreSQL context to write data
    with postgres_app.app_context():
        try:
            print("Dropping existing tables in PostgreSQL...")
            db.drop_all()
            print("Creating fresh tables in PostgreSQL...")
            db.create_all()
            
            # Insert data into PostgreSQL with explicit transaction
            print("Starting data migration to PostgreSQL...")
            
            # Insert subjects
            for subject_data in subjects_data:
                subject = Subject(**subject_data)
                db.session.add(subject)
            print(f"Added {len(subjects_data)} subjects")
            
            # Insert articles
            for article_data in articles_data:
                article = Article(**article_data)
                db.session.add(article)
            print(f"Added {len(articles_data)} articles")
            
            # Insert users
            for user_data in users_data:
                user = User(**user_data)
                db.session.add(user)
            print(f"Added {len(users_data)} users")
            
            # Commit all changes
            db.session.commit()
            print("Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error writing to PostgreSQL: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = migrate_data()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
