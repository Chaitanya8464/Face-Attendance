"""
Basic tests for the Flask application routes.

TODO: Add more comprehensive tests
TODO: Mock the face recognition calls for faster testing
TODO: Add integration tests with real database
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, Attendance


class TestRoutes(unittest.TestCase):
    """Test Flask routes"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_register_page(self):
        """Test register page loads"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
    
    def test_train_page(self):
        """Test train page loads"""
        response = self.client.get('/train')
        self.assertEqual(response.status_code, 200)
    
    def test_attendance_page(self):
        """Test attendance page loads"""
        response = self.client.get('/attendance')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_page(self):
        """Test dashboard page loads"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    # TODO: Test student registration
    # TODO: Test face upload endpoint
    # TODO: Test attendance recognition


class TestModels(unittest.TestCase):
    """Test database models"""
    
    def setUp(self):
        """Set up test database"""
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_student(self):
        """Test creating a student"""
        with self.app.app_context():
            student = Student(name='Test User', roll='TEST001')
            db.session.add(student)
            db.session.commit()
            
            found = Student.query.filter_by(roll='TEST001').first()
            self.assertIsNotNone(found)
            self.assertEqual(found.name, 'Test User')
    
    def test_student_roll_unique(self):
        """Test that roll numbers are unique"""
        with self.app.app_context():
            student1 = Student(name='Test User 1', roll='TEST001')
            student2 = Student(name='Test User 2', roll='TEST001')
            
            db.session.add(student1)
            db.session.commit()
            
            # This should fail due to unique constraint
            db.session.add(student2)
            with self.assertRaises(Exception):
                db.session.commit()
    
    def test_attendance_record(self):
        """Test creating attendance record"""
        with self.app.app_context():
            student = Student(name='Test User', roll='TEST001')
            db.session.add(student)
            db.session.commit()
            
            attendance = Attendance(student_id=student.id)
            db.session.add(attendance)
            db.session.commit()
            
            found = Attendance.query.first()
            self.assertIsNotNone(found)
            self.assertEqual(found.student_id, student.id)


if __name__ == '__main__':
    unittest.main()
