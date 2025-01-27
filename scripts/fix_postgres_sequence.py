import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db
from app.models import Article

def create_app():
    """Create a Flask app instance with Postgres configuration"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
    }
    db.init_app(app)
    return app

def fix_sequence():
    """Fix the sequence for article table in PostgreSQL"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get the maximum ID from the article table
            result = db.session.execute(text('SELECT MAX(id) FROM article')).scalar()
            max_id = result if result is not None else 0
            
            # Reset the sequence to start after the max ID
            db.session.execute(
                text(f"SELECT setval('article_id_seq', {max_id}, true)")
            )
            
            print(f"Successfully updated article_id_seq to continue from {max_id}")
            return True
            
        except Exception as e:
            print(f"Error updating sequence: {str(e)}")
            return False

if __name__ == '__main__':
    success = fix_sequence()
    if success:
        print("Sequence update completed successfully!")
    else:
        print("Sequence update failed!")
