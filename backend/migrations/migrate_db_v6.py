"""
Migration Script v6: Add marked_by columns to Attendance table

This migration adds columns to track which teacher/admin marked attendance.
Run this script once to update your database schema.

Usage:
    python migrate_db_v6.py
"""

import sys
import os

# Add the project directory to the path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from app import app
from models import db

def migrate():
    """Add marked_by columns to attendance table"""
    with app.app_context():
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('attendance')]
            
            if 'marked_by' in columns and 'marked_by_name' in columns:
                print("✓ Columns 'marked_by' and 'marked_by_name' already exist in attendance table")
                return
            
            # Add the new columns
            print("Adding 'marked_by' and 'marked_by_name' columns to attendance table...")
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE attendance ADD COLUMN marked_by INTEGER"
                ))
                conn.execute(db.text(
                    "ALTER TABLE attendance ADD COLUMN marked_by_name VARCHAR(100)"
                ))
                conn.commit()
            
            print("✓ Migration completed successfully!")
            print("\nNOTE: Existing attendance records will have NULL marked_by values.")
            print("New attendance records will automatically track who marked them.")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration v6")
    print("Adding marked_by columns to Attendance table")
    print("=" * 60)
    print()
    migrate()
    print()
    print("=" * 60)
    print("Migration completed!")
    print("=" * 60)
