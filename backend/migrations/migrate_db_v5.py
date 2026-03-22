"""
Migration Script v5: Add temporary_password column to Student table

This migration adds a column to store temporary passwords for CSV export.
Run this script once to update your database schema.

Usage:
    python migrate_db_v5.py
"""

import sys
import os

# Add the project directory to the path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from app import app
from models import db

def migrate():
    """Add temporary_password column to student table"""
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('student')]
            
            if 'temporary_password' in columns:
                print("✓ Column 'temporary_password' already exists in student table")
                return
            
            # Add the new column
            print("Adding 'temporary_password' column to student table...")
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE student ADD COLUMN temporary_password VARCHAR(50)"
                ))
                conn.commit()
            
            print("✓ Migration completed successfully!")
            print("\nNOTE: Existing students will have NULL temporary_password.")
            print("New student registrations will automatically store the temporary password.")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration v5")
    print("Adding temporary_password column to Student table")
    print("=" * 60)
    print()
    migrate()
    print()
    print("=" * 60)
    print("Migration completed!")
    print("=" * 60)
