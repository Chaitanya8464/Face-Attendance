"""
Migration Script v7: Add teacher_id column to User table

This migration adds a column to store unique teacher IDs (format: TF001, TF002, etc.)
Run this script once to update your database schema.

Usage:
    python migrate_db_v7.py
"""

import sys
import os

# Add the project directory to the path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from app import app
from models import db

def migrate():
    """Add teacher_id column to users table"""
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'teacher_id' in columns:
                print("✓ Column 'teacher_id' already exists in users table")
                return
            
            # Add the new column
            print("Adding 'teacher_id' column to users table...")
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE users ADD COLUMN teacher_id VARCHAR(10)"
                ))
                conn.commit()
            
            print("✓ Migration completed successfully!")
            print("\nNOTE: Existing teachers will have NULL teacher_id.")
            print("New teachers will automatically receive a teacher ID (format: TF001, TF002, etc.)")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration v7")
    print("Adding teacher_id column to Users table")
    print("=" * 60)
    print()
    migrate()
    print()
    print("=" * 60)
    print("Migration completed!")
    print("=" * 60)
