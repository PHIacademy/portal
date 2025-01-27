"""Add blob_url field to Article table"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
import sqlalchemy as sa
from sqlalchemy import create_engine

def upgrade():
    # Add blob_url column if it doesn't exist
    engine = db.engine
    inspector = sa.inspect(engine)
    
    with engine.connect() as conn:
        if 'blob_url' not in [c['name'] for c in inspector.get_columns('article')]:
            conn.execute(sa.text('ALTER TABLE article ADD COLUMN blob_url VARCHAR(500)'))
        conn.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        upgrade()
    print("Successfully added blob_url column to article table")
