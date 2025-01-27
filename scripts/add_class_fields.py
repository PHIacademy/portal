"""Add class and class number fields to users table"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
import sqlalchemy as sa
from sqlalchemy import create_engine
from flask import current_app

def upgrade():
    # Add new columns
    engine = db.engine
    inspector = sa.inspect(engine)
    
    with engine.connect() as conn:
        if 'class_name' not in [c['name'] for c in inspector.get_columns('user')]:
            conn.execute(sa.text('ALTER TABLE "user" ADD COLUMN class_name VARCHAR(20)'))
        
        if 'class_number' not in [c['name'] for c in inspector.get_columns('user')]:
            conn.execute(sa.text('ALTER TABLE "user" ADD COLUMN class_number INTEGER'))
        
        conn.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        upgrade()
    print("Successfully added class_name and class_number columns to user table")
