"""
Database Migration Script v2
Adds UID and training status columns to student table
"""
import sqlite3
import uuid

DATABASE = 'database.db'

def migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if uid column exists
        cursor.execute("PRAGMA table_info(student)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'uid' not in columns:
            print("Adding uid column to student table...")
            cursor.execute('ALTER TABLE student ADD COLUMN uid VARCHAR(36)')
            
            # Generate UIDs for existing students
            cursor.execute("SELECT id FROM student WHERE uid IS NULL")
            existing_students = cursor.fetchall()
            for student in existing_students:
                uid = str(uuid.uuid4())
                cursor.execute("UPDATE student SET uid = ? WHERE id = ?", (uid, student[0]))
                print(f"  Generated UID: {uid[:8]}... for student ID {student[0]}")
            
            print("✓ uid column added and populated")
        else:
            print("✓ uid column already exists")
        
        if 'is_trained' not in columns:
            print("Adding is_trained column...")
            cursor.execute('ALTER TABLE student ADD COLUMN is_trained BOOLEAN DEFAULT 0')
            print("✓ is_trained column added")
        else:
            print("✓ is_trained column already exists")
        
        if 'trained_at' not in columns:
            print("Adding trained_at column...")
            cursor.execute('ALTER TABLE student ADD COLUMN trained_at DATETIME')
            print("✓ trained_at column added")
        else:
            print("✓ trained_at column already exists")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        print("\nNOTE: Existing students have been assigned random UIDs.")
        print("You should re-register students for production use.")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=== Database Migration v2 ===\n")
    migrate()
    print("\nYou can now run: python app.py")
