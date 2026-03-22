"""
Database Models for Face Attendance System

Uses SQLAlchemy ORM for database operations.
Models:
    - User: Authentication and user management with roles
    - Student: Stores student info and face encodings
    - Attendance: Records attendance with timestamps

NOTE: Using SQLite for simplicity. For production with high concurrency,
      consider PostgreSQL or MySQL.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pickle  # Used to serialize the numpy array (face encoding)
import secrets

db = SQLAlchemy()


# ========================================
# USER MODEL - Authentication & Roles
# ========================================

class User(db.Model):
    """
    User model for authentication and role-based access control.
    
    Roles:
        - admin: Full system access, can manage users and teachers
        - teacher: Can manage students, view attendance, mark attendance
        - student: Can view own attendance only
    
    Attributes:
        id: Primary key
        email: Unique email for login
        username: Unique username
        password_hash: Hashed password
        role: User role (admin/teacher/student)
        is_verified: Email verification status
        is_active: Account active status
        created_at: Account creation timestamp
        last_login: Last login timestamp
        reset_token: Password reset token
        reset_token_expiry: Token expiration time
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    teacher_id = db.Column(db.String(10), unique=True, nullable=True)  # Unique teacher ID (e.g., TF001) - only for teachers
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationship to Student model (if user is a student)
    student_profile = db.relationship('Student', backref='user_account', uselist=False, lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a secure password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + datetime.timedelta(hours=1)
        return self.reset_token
    
    @staticmethod
    def verify_reset_token(token):
        """Verify if reset token is valid and not expired"""
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expiry and user.reset_token_expiry > datetime.utcnow():
            return user
        return None
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def is_teacher(self):
        """Check if user has teacher role"""
        return self.role == 'teacher'
    
    def is_student(self):
        """Check if user has student role"""
        return self.role == 'student'
    
    # Flask-Login required methods
    def get_id(self):
        """Return the user ID for Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    def is_active_property(self):
        """Return True if user account is active"""
        return self.is_active
    
    def is_anonymous(self):
        """Return False for authenticated users"""
        return False
    
    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"


# Custom type for storing the face encoding (a numpy array)
class EncodedFace(db.TypeDecorator):
    """
    Stores a face encoding (numpy array) as a BLOB in the database.
    
    Why custom type?
        NumPy arrays can't be stored directly in SQL, so we pickle them.
        This type decorator handles (de)serialization automatically.
    
    TODO: Consider using PostgreSQL's ARRAY type for better performance
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
    """
    Student model - stores registered students and their face encodings.

    Can be linked to a User account for student role access.

    Attributes:
        id: Primary key
        name: Student's full name
        roll: Unique roll number (used as identifier)
        uid: Unique generated ID (auto-generated)
        password_hash: Hashed password for student login
        user_id: Foreign key to User table (optional, for student accounts)
        email: Student email for receiving credentials (optional)
        face_encoding: 128-dimensional face embedding (numpy array)
        is_trained: Whether face has been trained/encoded
        trained_at: When face was trained
        added_on: Registration timestamp
        first_login: Whether this is student's first login (for password change enforcement)
        password_changed_at: When password was last changed
        credentials_sent: Whether credentials were sent to student
    """
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll = db.Column(db.String(20), unique=True, nullable=False)
    uid = db.Column(db.String(36), unique=True, nullable=False, index=True)  # Unique generated ID
    password_hash = db.Column(db.String(255), nullable=True)  # Hashed password for login
    temporary_password = db.Column(db.String(50), nullable=True)  # Store temporary password for export (cleared after password change)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)  # Student email
    # The face_encoding stores the 128-dimensional vector as a BLOB
    face_encoding = db.Column(EncodedFace, nullable=True)
    is_trained = db.Column(db.Boolean, default=False)  # Track if face is trained
    trained_at = db.Column(db.DateTime, nullable=True)  # When trained
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    first_login = db.Column(db.Boolean, default=True)  # Track first login for password change
    password_changed_at = db.Column(db.DateTime, nullable=True)  # Last password change
    credentials_sent = db.Column(db.Boolean, default=False)  # Track if credentials were sent

    # Relationship to attendance records
    # lazy=True means records are loaded when accessed (not upfront)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    
    def set_password(self, password):
        """Hash and set the student's password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        from werkzeug.security import check_password_hash
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Student('{self.roll}', '{self.name}')"
 
class Attendance(db.Model):
    """
    Attendance record - logs when a student marks attendance.

    Attributes:
        id: Primary key
        student_id: Foreign key to Student table
        timestamp: When attendance was marked (auto-set to now)
        marked_by: User ID of teacher/admin who marked attendance (nullable for self-marked)
        marked_by_name: Name of teacher/admin who marked attendance

    NOTE: Using datetime.now (not utcnow) to store local time.
          This might cause issues with DST - consider using timezone-aware datetimes.
    """
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who marked attendance
    marked_by_name = db.Column(db.String(100), nullable=True)  # Name of user who marked attendance

    def __repr__(self):
        return f"Attendance('{self.student_id}', '{self.timestamp}')"