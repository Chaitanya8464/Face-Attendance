from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle # Used to serialize the numpy array (face encoding)

db = SQLAlchemy()

# Custom type for storing the face encoding (a numpy array)
class EncodedFace(db.TypeDecorator):
    """
    Stores a face encoding (numpy array) as a BLOB in the database.
    """
    impl = db.LargeBinary

    def process_bind_param(self, value, dialect):
        """Convert numpy array to a bytes object for storage."""
        if value is not None:
            return pickle.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        """Convert bytes object back to a numpy array after retrieval."""
        if value is not None:
            return pickle.loads(value)
        return None

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll = db.Column(db.String(20), unique=True, nullable=False)
    # The face_encoding stores the 128-dimensional vector as a BLOB
    face_encoding = db.Column(EncodedFace, nullable=True) 
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to attendance records
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

    def __repr__(self):
        return f"Student('{self.roll}', '{self.name}')"
 
class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Attendance('{self.student_id}', '{self.timestamp}')"