"""
Database Migration Script - Add Student Password Management Fields

This script adds the following columns to the 'student' table:
    - email: Student email for receiving credentials (optional)
    - first_login: Whether this is student's first login (default=True)
    - password_changed_at: When password was last changed
    - credentials_sent: Whether credentials were sent to student

Usage:
    python migrate_db_v4.py

NOTE: Backup your database before running this script!
"""
import sqlite3
from datetime import datetime

DATABASE = 'database.db'


def migrate():
    """Run database migration"""
    print("=" * 60)
    print("Database Migration v4 - Student Password Management Fields")
    print("=" * 60)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(student)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add email column (without UNIQUE constraint initially)
        if 'email' not in columns:
            print("\n[1/4] Adding 'email' column...")
            cursor.execute('''
                ALTER TABLE student ADD COLUMN email VARCHAR(120)
            ''')
            print("      ✓ Column 'email' added successfully")
            
            # Create unique index separately
            print("      Creating unique index on email...")
            try:
                cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_student_email_unique ON student(email) WHERE email IS NOT NULL')
                print("      ✓ Unique index created successfully")
            except Exception as e:
                print(f"      ⚠ Index creation skipped: {e}")
        else:
            print("\n[1/4] Column 'email' already exists, skipping...")
        
        # Add first_login column
        if 'first_login' not in columns:
            print("\n[2/4] Adding 'first_login' column...")
            cursor.execute('''
                ALTER TABLE student ADD COLUMN first_login BOOLEAN DEFAULT 1
            ''')
            print("      ✓ Column 'first_login' added successfully")
        else:
            print("\n[2/4] Column 'first_login' already exists, skipping...")
        
        # Add password_changed_at column
        if 'password_changed_at' not in columns:
            print("\n[3/4] Adding 'password_changed_at' column...")
            cursor.execute('''
                ALTER TABLE student ADD COLUMN password_changed_at DATETIME
            ''')
            print("      ✓ Column 'password_changed_at' added successfully")
        else:
            print("\n[3/4] Column 'password_changed_at' already exists, skipping...")
        
        # Add credentials_sent column
        if 'credentials_sent' not in columns:
            print("\n[4/4] Adding 'credentials_sent' column...")
            cursor.execute('''
                ALTER TABLE student ADD COLUMN credentials_sent BOOLEAN DEFAULT 0
            ''')
            print("      ✓ Column 'credentials_sent' added successfully")
        else:
            print("\n[4/4] Column 'credentials_sent' already exists, skipping...")
        
        # Update existing students to have first_login=False (they've already logged in before)
        print("\n[5/5] Updating existing students...")
        cursor.execute('''
            UPDATE student 
            SET first_login = 0, password_changed_at = ?
            WHERE first_login IS NULL OR first_login = 1
        ''', (datetime.utcnow(),))
        updated = cursor.rowcount
        print(f"      ✓ Updated {updated} existing student(s)")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        print("Database has been rolled back to previous state.")
        raise
    
    finally:
        conn.close()


if __name__ == '__main__':
    migrate()
