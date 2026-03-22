"""
Test script to create a test student for demonstration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, Student

with app.app_context():
    # Check if test student exists
    test_student = Student.query.filter_by(roll='TEST001').first()
    
    if test_student:
        print(f"✓ Test student already exists:")
        print(f"  Name: {test_student.name}")
        print(f"  Roll: {test_student.roll}")
        print(f"  UID: {test_student.uid}")
        print(f"  Email: {test_student.email}")
        print(f"\n  Login at: http://localhost:8000/student-login")
    else:
        # Create a test student
        import uuid
        from werkzeug.security import generate_password_hash
        
        uid = str(uuid.uuid4())
        password = "test1234"
        
        student = Student(
            name="Test Student",
            roll="TEST001",
            uid=uid,
            email="test@student.com",
            first_login=False
        )
        student.password_hash = generate_password_hash(password)
        
        db.session.add(student)
        db.session.commit()
        
        print(f"✓ Test student created successfully!")
        print(f"\n  Name: {test_student.name if test_student else student.name}")
        print(f"  Roll: TEST001")
        print(f"  UID: {uid}")
        print(f"  Password: {password}")
        print(f"  Email: test@student.com")
        print(f"\n  Login at: http://localhost:8000/student-login")
        print(f"  Dashboard: http://localhost:8000/student-dashboard")
