import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def add_users_table():
    """Add users table to the database without affecting existing data."""
    # Connect to the database
    conn = sqlite3.connect('instance/educational_portal.db')
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            last_login DATETIME,
            role VARCHAR(20) DEFAULT 'student',
            auth_provider VARCHAR(20) DEFAULT 'local',
            auth_provider_id VARCHAR(255),
            reset_password_token VARCHAR(100),
            reset_password_expires DATETIME,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            profile_picture VARCHAR(255),
            bio TEXT
        )
        ''')
        
        # Create indexes for frequently accessed columns
        cursor.execute('CREATE INDEX idx_user_email ON user(email)')
        cursor.execute('CREATE INDEX idx_user_username ON user(username)')
        
        # Create default admin user
        admin_password = 'admin123'
        admin_password_hash = generate_password_hash(admin_password)
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO user (
            email, username, password_hash, role, 
            first_name, last_name, is_active, created_at
        ) VALUES (
            'admin@example.com', 'admin', ?, 'admin',
            'Admin', 'User', 1, ?
        )
        ''', (admin_password_hash, current_time))
        
        # Commit changes
        conn.commit()
        print("Users table created successfully!")
        print("\nDefault admin user created:")
        print("Email: admin@example.com")
        print("Password: admin123")
        
    except sqlite3.OperationalError as e:
        if 'already exists' in str(e):
            print("Users table already exists.")
        else:
            print(f"Error: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    # Set up Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.environ["PYTHONPATH"] = project_root
    
    add_users_table()