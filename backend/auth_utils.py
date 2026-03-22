"""
Authentication Utilities for Face Attendance System

Provides:
    - Login required decorator
    - Role-based access control decorators
    - Email verification utilities
    - Password reset utilities
"""
from functools import wraps
from flask import redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    Redirects non-admin users to dashboard or login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def teacher_required(f):
    """
    Decorator to restrict access to teacher and admin users.
    Students are redirected to their dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if current_user.is_student():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def student_required(f):
    """
    Decorator to restrict access to student users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_student():
            flash('This page is for students only.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def verified_required(f):
    """
    Decorator to ensure user has verified their email.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_verified:
            flash('Please verify your email to access this page.', 'warning')
            return redirect(url_for('verify_email'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def update_last_login(user):
    """Update user's last login timestamp"""
    user.last_login = datetime.utcnow()
    db.session.commit()


def get_user_role_name(role):
    """Get human-readable role name"""
    role_names = {
        'admin': 'Administrator',
        'teacher': 'Teacher',
        'student': 'Student'
    }
    return role_names.get(role, 'Unknown')
