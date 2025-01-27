import os
import shutil
from datetime import datetime

def backup_database():
    """Create a backup of the SQLite database."""
    # Source database path
    db_path = 'instance/educational_portal.db'
    
    # Create backups directory if it doesn't exist
    backup_dir = 'instance/backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{backup_dir}/educational_portal_{timestamp}.db'
    
    try:
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        print(f"Database backup created successfully at: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False

if __name__ == '__main__':
    backup_database()