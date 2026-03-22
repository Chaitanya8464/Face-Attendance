"""
Database Migration Script v3
Adds password_hash column to student table for student login
"""
import sqlite3

DATABASE = 'database.db'

def migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if password_hash column exists
        cursor.execute("PRAGMA table_info(student)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("Adding password_hash column to student table...")
            cursor.execute('ALTER TABLE student ADD COLUMN password_hash VARCHAR(255)')
            print("✓ password_hash column added")
            print("\nNOTE: Existing students will need password reset.")
            print("Admin should update passwords for existing students.")
        else:
            print("✓ password_hash column already exists")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=== Database Migration v3 ===\n")
    migrate()
    print("\nYou can now run: python app.py")
