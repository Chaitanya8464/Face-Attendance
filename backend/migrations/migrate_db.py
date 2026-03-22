"""
Database Migration Script
Adds user_id column to student table for authentication system
"""
import sqlite3
from datetime import datetime

DATABASE = 'database.db'

def migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(student)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to student table...")
            cursor.execute('ALTER TABLE student ADD COLUMN user_id INTEGER')
            print("✓ user_id column added")
        else:
            print("✓ user_id column already exists")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'student',
                    is_verified BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    reset_token VARCHAR(100),
                    reset_token_expiry DATETIME
                )
            ''')
            print("✓ users table created")
        else:
            print("✓ users table already exists")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=== Database Migration ===\n")
    migrate()
    print("\nYou can now run: python app.py")
