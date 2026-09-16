import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check if status column exists
cursor.execute("PRAGMA table_info(attendance)")
columns = [col[1] for col in cursor.fetchall()]
print('Current columns:', columns)

if 'status' not in columns:
    print('Adding status column...')
    cursor.execute("ALTER TABLE attendance ADD COLUMN status VARCHAR(20) DEFAULT 'present'")
    conn.commit()
    print('Column added successfully!')
else:
    print('Status column already exists')

conn.close()