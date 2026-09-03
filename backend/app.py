"""
Face Recognition Attendance System
Main Flask application - handles routes and business logic

TODO: Refactor database initialization to use Flask-Migrate
FIXME: Camera recognition sometimes fails on first attempt - needs retry logic
"""
import os
import base64
import io
import csv
import numpy as np
import cv2
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, Response, flash, session
from flask_login import login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# --- Flask & Database Setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_ROOT = os.path.join(BASE_DIR, '..', 'frontend')  # frontend is at same level as backend

# Import models and utilities
from models import db, Student, Attendance, User, Notification, RectificationRequest
from face_utils import encode_faces, recognize_faces_from_frame, save_base64_image
from auth_utils import login_manager, admin_required, teacher_required, verified_required, update_last_login
from email_utils import mail, send_verification_email, send_password_reset_email, send_welcome_email, send_attendance_notification, send_low_attendance_notification, send_attendance_marked_to_admin, create_notification, send_rectification_request_to_admin, send_rectification_decision_to_teacher, send_rectification_notification_to_student

app = Flask(__name__,
            template_folder=FRONTEND_ROOT,
            static_folder=os.path.join(FRONTEND_ROOT, 'static'))

# Database configuration - use PostgreSQL on Render, SQLite for local development
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render PostgreSQL - replace postgres:// with postgresql:// for SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Local development with SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')

# Email configuration (for password reset and verification)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@faceattendance.com')

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# Make current_user available in all templates
@app.context_processor
def inject_user():
    from flask_login import current_user
    return dict(current_user=current_user)

# --- Ensure tables exist and create admin user ---
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email='admin@faceattendance.com',
            username='admin',
            role='admin',
            is_verified=True
        )
        admin.set_password('admin123')  # Default password - change in production!
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin@faceattendance.com / admin123")


# -----------------------
# ROUTES
# -----------------------

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    # Added for Railway deployment checks
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def index():
    # Redirect logged-in users to their appropriate dashboard
    if session.get('student_id'):
        return redirect(url_for('student_dashboard'))
    elif current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ========================================
# STUDENT LOGIN & DASHBOARD
# ========================================

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    """Student login with UID and password"""
    from flask_login import login_user

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        uid = request.form.get('uid', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not (uid and password):
            return render_template('student_login.html', error='UID and password required')

        # Find student by UID
        student = Student.query.filter_by(uid=uid).first()

        if student and student.check_password(password):
            # Create a temporary user session for the student
            # Link to User table if exists, otherwise create temporary access
            user = User.query.filter_by(id=student.user_id).first()

            if user and user.is_student():
                # Keep the student session available to the student-specific
                # dashboard, profile, and first-login password flow.
                session['student_id'] = student.id
                session['student_name'] = student.name
                session['student_roll'] = student.roll
                login_user(user, remember=remember)
                flash(f'Welcome back, {student.name}!', 'success')

                # Check if first login - force password change
                if student.first_login:
                    session['pending_student_id'] = student.id
                    flash('Please change your password to continue.', 'warning')
                    return redirect(url_for('student_change_password'))

                return redirect(url_for('dashboard'))
            else:
                # Student doesn't have a user account, create temporary session
                # For now, just redirect to student dashboard with student info in session
                session['student_id'] = student.id
                session['student_name'] = student.name
                session['student_roll'] = student.roll

                # Check if first login - force password change
                if student.first_login:
                    flash('Please change your temporary password to continue.', 'warning')
                    return redirect(url_for('student_change_password'))

                flash(f'Welcome, {student.name}!', 'success')
                return redirect(url_for('student_dashboard'))
        else:
            return render_template('student_login.html', error='Invalid UID or password')

    return render_template('student_login.html')


@app.route('/student-dashboard')
def student_dashboard():
    """Student dashboard to view own attendance"""
    if 'student_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    student = Student.query.get(student_id)

    if not student:
        session.pop('student_id', None)
        flash('Student not found.', 'error')
        return redirect(url_for('student_login'))

    # Get student's attendance records
    attendance_records = Attendance.query.filter_by(student_id=student_id)\
                                        .order_by(Attendance.timestamp.desc())\
                                        .limit(100).all()

    # Calculate stats
    total_attendance = len(attendance_records)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_attendance = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.timestamp >= today_start
    ).first()

    # Calculate attendance percentage
    total_attendance_days = db.session.query(db.func.count(db.func.distinct(
        db.func.date(Attendance.timestamp)
    ))).filter_by(student_id=student_id).scalar() or 0
    days_in_period = 30
    attendance_percentage = (total_attendance_days / days_in_period * 100) if days_in_period > 0 else 0
    attendance_percentage = min(100, attendance_percentage)

    return render_template('dashboard_student.html',
                         student=student,
                         attendance=attendance_records,
                         total_attendance=total_attendance,
                         attendance_percentage=round(attendance_percentage, 1),
                         marked_today=bool(today_attendance))


@app.route('/student-logout')
def student_logout():
    """Student logout"""
    session.pop('student_id', None)
    session.pop('student_name', None)
    session.pop('student_roll', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('student_login'))


# ========================================
# STUDENT ATTENDANCE HISTORY
# ========================================

@app.route('/student/attendance')
def student_attendance_history():
    """Student view of their own attendance history with marked_by info"""
    if 'student_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    student = Student.query.get(student_id)

    if not student:
        session.pop('student_id', None)
        flash('Student not found.', 'error')
        return redirect(url_for('student_login'))

    # Get all attendance records for this student
    attendance_records = Attendance.query.filter_by(student_id=student_id)\
                                        .order_by(Attendance.timestamp.desc())\
                                        .all()

    # Calculate stats
    total_attendance = len(attendance_records)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_attendance = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.timestamp >= today_start
    ).first()

    # Calculate attendance percentage
    total_attendance_days = db.session.query(db.func.count(db.func.distinct(
        db.func.date(Attendance.timestamp)
    ))).filter_by(student_id=student_id).scalar() or 0
    days_in_period = 30
    attendance_percentage = (total_attendance_days / days_in_period * 100) if days_in_period > 0 else 0
    attendance_percentage = min(100, attendance_percentage)

    return render_template('attendance_history.html',
                         student=student,
                         attendance=attendance_records,
                         total_attendance=total_attendance,
                         attendance_percentage=round(attendance_percentage, 1),
                         marked_today=bool(today_attendance))


# ========================================
# STUDENT PASSWORD MANAGEMENT
# ========================================

@app.route('/student/change-password', methods=['GET', 'POST'])
def student_change_password():
    """Student change password page"""
    if 'student_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    student = Student.query.get(student_id)

    if not student:
        session.pop('student_id', None)
        flash('Student not found.', 'error')
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate current password
        if not student.check_password(current_password):
            return render_template('change_password.html', student=student, error='Current password is incorrect')

        # Validate new password
        if not new_password:
            return render_template('change_password.html', student=student, error='New password is required')

        if len(new_password) < 6:
            return render_template('change_password.html', student=student, error='Password must be at least 6 characters')

        if new_password != confirm_password:
            return render_template('change_password.html', student=student, error='Passwords do not match')

        # Update password
        student.set_password(new_password)
        student.first_login = False  # Mark as not first login anymore
        student.password_changed_at = datetime.utcnow()
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('change_password.html', student=student)


@app.route('/student/forgot-password', methods=['GET', 'POST'])
def student_forgot_password():
    """Student forgot password - request reset"""
    if request.method == 'POST':
        uid = request.form.get('uid', '').strip()
        email = request.form.get('email', '').strip()

        if not (uid and email):
            return render_template('forgot_password.html', error='UID and email are required')

        # Find student by UID and email
        student = Student.query.filter_by(uid=uid, email=email).first()

        if student:
            # Generate reset token
            from itsdangerous import URLSafeTimedSerializer
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(uid, salt='student-password-reset')

            # Send reset email
            try:
                from email_utils import send_student_password_reset_email
                send_student_password_reset_email(student, token)
                flash('Password reset link sent to your email.', 'success')
            except Exception as e:
                print(f"Email send failed: {e}")
                # Fallback: show token for testing
                flash(f'Email configuration not available. Reset token: {token}', 'info')
        else:
            # Don't reveal if UID/email exists
            flash('If the UID and email match, a reset link has been sent.', 'info')

        return redirect(url_for('student_login'))

    return render_template('forgot_password.html')


@app.route('/student/reset-password/<token>', methods=['GET', 'POST'])
def student_reset_password(token):
    """Student reset password with token"""
    from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
    
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    
    try:
        uid = serializer.loads(token, salt='student-password-reset', max_age=3600)  # 1 hour
        student = Student.query.filter_by(uid=uid).first()
        
        if not student:
            flash('Invalid reset link.', 'error')
            return redirect(url_for('student_forgot_password'))
        
        if request.method == 'POST':
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not new_password:
                return render_template('reset_password.html', token=token, error='Password is required')

            if len(new_password) < 6:
                return render_template('reset_password.html', token=token, error='Password must be at least 6 characters')

            if new_password != confirm_password:
                return render_template('reset_password.html', token=token, error='Passwords do not match')

            # Update password
            student.set_password(new_password)
            student.first_login = False
            student.password_changed_at = datetime.utcnow()
            db.session.commit()

            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('student_login'))

        return render_template('reset_password.html', token=token, student=student)
        
    except SignatureExpired:
        flash('Reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('student_forgot_password'))
    except BadSignature:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('student_forgot_password'))


@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    """Student profile page - view and edit details"""
    if 'student_id' not in session:
        flash('Please login to access your profile.', 'warning')
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    student = Student.query.get(student_id)

    if not student:
        session.pop('student_id', None)
        flash('Student not found.', 'error')
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()

        if not name:
            return render_template('profile.html', student=student, error='Name is required')

        # Update student details
        student.name = name
        if email:
            # Check if email is already taken by another student
            existing = Student.query.filter_by(email=email).first()
            if existing and existing.id != student.id:
                return render_template('profile.html', student=student, error='Email already registered')
        student.email = email or None

        db.session.commit()

        # Update session
        session['student_name'] = name

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))

    return render_template('profile.html', student=student)


# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    from flask_login import login_user
    from auth_utils import update_last_login
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not (email and password):
            return render_template('login.html', error='Email and password required')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                return render_template('login.html', error='Account is deactivated')

            login_user(user, remember=remember)
            update_last_login(user)

            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/verify-email')
def verify_email():
    """Email verification page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if current_user.is_verified:
        flash('Email already verified.', 'info')
        return redirect(url_for('dashboard'))
    
    # Resend verification email
    try:
        send_verification_email(current_user)
        flash('Verification email sent! Please check your inbox.', 'info')
    except:
        flash('Could not send verification email. Please try again later.', 'error')

    return render_template('verify_email.html')


@app.route('/verify-email/<token>')
def verify_email_token(token):
    """Verify email with token"""
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    
    try:
        email = serializer.loads(token, salt='email-verification', max_age=86400)  # 24 hours
        user = User.query.filter_by(email=email).first()
        
        if user and not user.is_verified:
            user.is_verified = True
            db.session.commit()
            flash('Email verified successfully!', 'success')
            return redirect(url_for('login'))
        elif user and user.is_verified:
            flash('Email already verified.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification link.', 'error')
            return redirect(url_for('signup'))
    
    except SignatureExpired:
        flash('Verification link has expired. Please sign up again.', 'error')
        return redirect(url_for('signup'))
    except BadSignature:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('signup'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            return render_template('forgot_password.html', error='Email is required')

        user = User.query.filter_by(email=email).first()

        if user:
            try:
                send_password_reset_email(user)
                flash('Password reset link sent to your email.', 'success')
            except Exception as e:
                print(f"Email send failed: {e}")
                flash('Could not send reset email. Please try again later.', 'error')
        else:
            # Don't reveal if email exists or not (security)
            flash('If the email exists, a reset link has been sent.', 'info')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset page with token"""
    user = User.verify_reset_token(token)
    
    if not user:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not password:
            return render_template('reset_password.html', error='Password is required', token=token)

        if len(password) < 6:
            return render_template('reset_password.html', error='Password must be at least 6 characters', token=token)

        if password != confirm_password:
            return render_template('reset_password.html', error='Passwords do not match', token=token)

        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Password reset successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token, username=user.username)


# ========================================
# DASHBOARD (Role-based)
# ========================================

@app.route('/dashboard')
def dashboard():
    """Main dashboard - redirects based on user role"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Role-based dashboard rendering
    if current_user.is_admin():
        return render_template('dashboard_admin.html')
    elif current_user.is_teacher():
        return render_template('dashboard_teacher.html')
    else:  # student
        return redirect(url_for('student_dashboard'))


@app.route('/notifications')
@teacher_required
def notifications():
    """Notifications page for admin/teacher"""
    return render_template('notifications.html')


@app.route('/admin/attendance/rectify')
@admin_required
def admin_attendance_rectify():
    """Attendance rectification page for admin"""
    return render_template('attendance_rectify.html')


@app.route('/admin/rectification/requests')
@admin_required
def admin_rectification_requests():
    """Admin page to review rectification requests"""
    return render_template('rectification_admin.html')


@app.route('/teacher/rectification/requests')
@teacher_required
def teacher_rectification_requests():
    """Teacher page to view their rectification requests"""
    return render_template('rectification_teacher.html')


# -----------------------
# Register Student (Admin only)
# -----------------------

def generate_student_uid():
    """
    Generate a unique UID for new students.
    Format: 26FACE followed by 5-digit sequential number (e.g., 26FACE00001)
    """
    # Get the last student by ID to find the next sequence number
    last_student = Student.query.order_by(Student.id.desc()).first()
    
    if last_student and last_student.uid and last_student.uid.startswith('26FACE'):
        # Extract the numeric part from the last UID
        try:
            last_number = int(last_student.uid[6:])  # Get digits after '26FACE'
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        # First student with new format or no students yet
        next_number = 1
    
    # Format as 26FACE followed by 5-digit zero-padded number
    return f"26FACE{next_number:05d}"


@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    """Admin-only student registration with unique UID and password generation"""
    import secrets

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll = request.form.get('roll', '').strip()
        email = request.form.get('email', '').strip()

        if not (name and roll):
            return render_template('register.html', error='Name and Roll are required')

        # Check for duplicate roll numbers
        existing = Student.query.filter_by(roll=roll).first()
        if existing:
            return render_template('register.html', error='Roll number already exists')

        # Generate unique UID and temporary password
        uid = generate_student_uid()
        password = secrets.token_urlsafe(8)  # Generate random 8-character password

        student = Student(name=name, roll=roll, uid=uid, email=email if email else None)
        student.set_password(password)  # Hash the password
        student.temporary_password = password  # Store temporary password for export
        db.session.add(student)
        db.session.commit()

        # Send credentials email if email provided
        if email:
            try:
                send_student_credentials_email(student, password)
                student.credentials_sent = True
                db.session.commit()
                flash(f'Student registered successfully! Credentials sent to {email}', 'success')
            except Exception as e:
                print(f"Failed to send credentials email: {e}")
                flash('Student registered! Email sending failed. Show credentials below.', 'warning')
        else:
            flash('Student registered successfully!', 'success')

        # Store credentials in session to show in modal
        session['new_student_credentials'] = {
            'uid': uid,
            'password': password,
            'name': name,
            'roll': roll,
            'email': email
        }
        return redirect(url_for('show_credentials'))

    return render_template('register.html')


@app.route('/show-credentials')
@admin_required
def show_credentials():
    """Show generated credentials for newly registered student"""
    credentials = session.pop('new_student_credentials', None)
    if not credentials:
        return redirect(url_for('admin_students'))

    return render_template('credentials.html', credentials=credentials)


# -----------------------
# Camera Test Page (Diagnostic)
# -----------------------
@app.route('/camera-test')
def camera_test():
    """Camera diagnostic test page - useful for troubleshooting"""
    return render_template('camera_test.html')


# -----------------------
# Capture Face Photos
# -----------------------
@app.route('/capture/<roll>')
@admin_required
def capture(roll):
    """Admin-only face capture for student registration"""
    student = Student.query.filter_by(roll=roll).first()
    if not student:
        return redirect(url_for('register'))
    return render_template('capture.html', roll=roll, student=student)


@app.route('/api/upload_face', methods=['POST'])
def api_upload_face():
    """
    Expects JSON:
    {
      "roll": "<roll>",
      "image": "data:image/jpeg;base64,..."
    }
    Saves the image to dataset/<roll>/<count>.jpg

    Note: Using JSON instead of multipart form for easier client-side handling
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        roll = data.get('roll')
        image_b64 = data.get('image')

        if not roll:
            return jsonify({'error': 'Missing roll number'}), 400
        
        if not image_b64:
            return jsonify({'error': 'Missing image data'}), 400

        # Validate image data format
        if not image_b64.startswith('data:image'):
            print(f"[WARNING] Invalid image format. Expected data URI, got: {image_b64[:50]}...")
            return jsonify({'error': 'Invalid image format. Expected base64 data URI'}), 400

        print(f"[INFO] Uploading face image for roll: {roll}")
        
        saved_path = save_base64_image(image_b64, roll)
        
        if not saved_path:
            print(f"[ERROR] Failed to save image for roll: {roll}")
            return jsonify({'error': 'Failed to save image. Check server logs.'}), 500
        
        filename = os.path.basename(saved_path)
        print(f"[INFO] Image saved successfully: {filename}")

        return jsonify({'saved': filename}), 200

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


# -----------------------
# Train Model (Encode Faces)
# -----------------------
@app.route('/train')
@admin_required
def train():
    """Admin-only face training - encodes faces and marks students as trained"""
    try:
        from datetime import datetime
        data = encode_faces()
        total = len(data.get('encodings', [])) if data else 0
        
        # Keep every student's training status in sync with the encodings that
        # were successfully generated during this training run.
        rolls_trained = set(data.get('rolls', []))
        for student in Student.query.all():
            student.is_trained = student.roll in rolls_trained
            student.trained_at = datetime.utcnow() if student.is_trained else None
        db.session.commit()

        return render_template('train.html', total=total, trained_count=len(rolls_trained))
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        # TODO: Show more detailed error message to user
        return render_template('train.html', total=0, error="Training failed. Check dataset and face_utils.py.")


# -----------------------
# Attendance Page
# -----------------------
@app.route('/attendance')
def attendance_page():
    # Students may mark their own attendance from a student session. Staff can
    # mark attendance for the group. Anonymous access is not permitted.
    if not session.get('student_id') and not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('attendance.html')


# -----------------------
# Real-Time Recognition (server webcam)
# -----------------------
@app.route('/api/start_recognize', methods=['POST'])
def api_start_recognize():
    """
    Captures a frame from the server webcam and recognizes faces.

    NOTE: This is for server-side camera only. Client-side uses /api/recognize_attendance
    """
    try:
        if not current_user.is_authenticated or current_user.is_student():
            return jsonify({'error': 'Staff login required for server-camera recognition'}), 403

        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()

        if not ret:
            return jsonify({'error': 'Camera not available'}), 500

        results = recognize_faces_from_frame(frame)
        marked = []

        # Get current user if logged in (teacher/admin)
        marked_by_user_id = None
        marked_by_name = None
        if current_user.is_authenticated:
            marked_by_user_id = current_user.id
            marked_by_name = current_user.username

        for res in results:
            roll = res.get('name')
            if roll and roll != 'Unknown':
                student = Student.query.filter_by(roll=roll).first()
                if student:
                    # Prevent duplicate attendance for same day
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_att = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.timestamp >= today_start
                    ).first()

                    if not existing_att:
                        att = Attendance(
                            student_id=student.id,
                            marked_by=marked_by_user_id,
                            marked_by_name=marked_by_name
                        )
                        db.session.add(att)
                        db.session.commit()
                        marked.append({'roll': student.roll, 'name': student.name})

        return jsonify({'marked': marked}), 200

    except Exception as e:
        print(f"[ERROR] Recognition failed: {e}")
        return jsonify({'error': 'Recognition failed'}), 500


def check_and_send_low_attendance_alert(student, threshold=75):
    """
    Check if student's attendance is below threshold and send notification.
    
    Args:
        student: Student object
        threshold: Attendance percentage threshold (default 75%)
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Calculate attendance for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    total_days = db.session.query(func.count(func.distinct(
        func.date(Attendance.timestamp)
    ))).filter(
        Attendance.student_id == student.id,
        Attendance.timestamp >= thirty_days_ago
    ).scalar() or 0
    
    # 30 days = ~22 working days (assuming 5 days/week)
    working_days = 22
    attendance_percentage = (total_days / working_days * 100) if working_days > 0 else 0
    attendance_percentage = min(100, attendance_percentage)
    
    if attendance_percentage < threshold:
        # Check if we already sent a low attendance notification recently (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_notif = Notification.query.filter(
            Notification.student_id == student.id,
            Notification.type == 'low_attendance',
            Notification.created_at >= week_ago
        ).first()
        
        if not recent_notif:
            # Send email to student
            try:
                send_low_attendance_notification(student, round(attendance_percentage, 1), threshold)
            except Exception as e:
                print(f"Failed to send low attendance email: {e}")
            
            # Create in-app notification for admins
            try:
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    create_notification(
                        user_id=admin.id,
                        student_id=student.id,
                        notif_type='low_attendance',
                        title=f'Low Attendance Alert: {student.name}',
                        message=f'{student.name} ({student.roll}) attendance is {attendance_percentage:.1f}% (below {threshold}% threshold)'
                    )
            except Exception as e:
                print(f"Failed to create low attendance notification: {e}")
            
            return True
    return False


# -----------------------
# Client Image Recognition (browser upload)
# -----------------------
@app.route('/api/recognize_attendance', methods=['POST'])
def api_recognize_attendance():
    """
    Receives a base64 image from the client, recognizes faces, and marks attendance.

    This is the main attendance endpoint used by the browser camera.
    Only trained students can mark attendance.
    Prevents duplicate entries for the same student on the same day.
    Tracks which teacher/admin marked the attendance.
    """
    try:
        session_student_id = session.get('student_id')
        linked_student_id = None
        if current_user.is_authenticated and current_user.is_student():
            linked_student = Student.query.filter_by(user_id=current_user.id).first()
            linked_student_id = linked_student.id if linked_student else None

        allowed_student_id = session_student_id or linked_student_id
        if not allowed_student_id and not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 401

        data = request.get_json()
        image_b64 = data.get('image')

        if not image_b64:
            return jsonify({'error': 'No image provided'}), 400

        # Decode base64
        if ',' in image_b64:
            image_b64 = image_b64.split(',', 1)[1]
        image_data = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = recognize_faces_from_frame(frame)
        recognized = []
        unrecognized = []

        # Get current user if logged in (teacher/admin)
        marked_by_user_id = None
        marked_by_name = None
        if current_user.is_authenticated:
            marked_by_user_id = current_user.id
            marked_by_name = current_user.username

        for res in results:
            roll = res.get('name')
            box = res.get('box')
            if roll and roll != 'Unknown':
                student = Student.query.filter_by(roll=roll).first()
                if student:
                    # A student session can only mark the logged-in student's
                    # attendance. Staff sessions may mark any recognized student.
                    if allowed_student_id and student.id != allowed_student_id:
                        continue

                    # Only allow trained students to mark attendance
                    if not student.is_trained:
                        continue  # Skip untrained students

                    # Prevent duplicate attendance for same day
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # For students: prevent any duplicate for the day
                    # For teachers/admins: prevent duplicate only for this teacher (they can mark even if another teacher already did)
                    if allowed_student_id:
                        # Student marking their own attendance - global duplicate check
                        existing_att = Attendance.query.filter(
                            Attendance.student_id == student.id,
                            Attendance.timestamp >= today_start
                        ).first()
                    else:
                        # Teacher/admin marking attendance - per-teacher duplicate check
                        existing_att = Attendance.query.filter(
                            Attendance.student_id == student.id,
                            Attendance.timestamp >= today_start,
                            Attendance.marked_by == marked_by_user_id
                        ).first()

                    if not existing_att:
                        att = Attendance(
                            student_id=student.id,
                            marked_by=marked_by_user_id,
                            marked_by_name=marked_by_name
                        )
                        db.session.add(att)
                        db.session.commit()

                        # Send notifications
                        marked_at = datetime.now()
                        
                        # 1. Send email to student
                        try:
                            send_attendance_notification(student, marked_by_name or 'Self', marked_at)
                        except Exception as e:
                            print(f"Failed to send student notification: {e}")
                        
                        # 2. Create in-app notification for admins
                        try:
                            admins = User.query.filter_by(role='admin').all()
                            for admin in admins:
                                create_notification(
                                    user_id=admin.id,
                                    student_id=student.id,
                                    notif_type='attendance_marked',
                                    title=f'Attendance Marked: {student.name}',
                                    message=f'Attendance marked for {student.name} ({student.roll}) by {marked_by_name or "Self"} at {marked_at.strftime("%Y-%m-%d %H:%M:%S")}'
                                )
                                # Also send email to admin
                                send_attendance_marked_to_admin(admin, student, marked_by_name or 'Self', marked_at)
                        except Exception as e:
                            print(f"Failed to create admin notification: {e}")
                        
                        # 3. Check for low attendance and send alert
                        try:
                            check_and_send_low_attendance_alert(student)
                        except Exception as e:
                            print(f"Failed to check low attendance: {e}")

                    recognized.append({
                        'roll': student.roll,
                        'name': student.name,
                        'uid': student.uid,
                        'box': box
                    })
            else:
                # Unrecognized face detected
                unrecognized.append({
                    'box': box
                })

        return jsonify({
            'recognized': recognized,
            'unrecognized': unrecognized
        }), 200

    except Exception as e:
        print(f"[ERROR] Attendance recognition failed: {e}")
        return jsonify({'error': 'Recognition failed'}), 500


# -----------------------
# API: Stats for Homepage
# -----------------------
@app.route('/api/stats')
def api_stats():
    """Get quick stats for homepage"""
    total_students = Student.query.count()
    total_records = Attendance.query.count()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_attendance = Attendance.query.filter(Attendance.timestamp >= today_start).count()

    # Check if model is trained
    model_trained = os.path.exists(os.path.join(BASE_DIR, 'encodings.pkl'))

    return jsonify({
        'total_students': total_students,
        'today_attendance': today_attendance,
        'total_records': total_records,
        'model_trained': model_trained
    })


# -----------------------
# API: Notifications
# -----------------------
@app.route('/api/notifications', methods=['GET'])
@teacher_required
def api_get_notifications():
    """Get notifications for current user (admin/teacher)"""
    user_id = current_user.id
    is_admin = current_user.is_admin()
    
    # For admins, show all notifications
    # For teachers, show notifications related to students they've marked
    if is_admin:
        notifications = Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(50).all()
    else:
        # Get students this teacher has marked attendance for
        marked_student_ids = db.session.query(
            Attendance.student_id
        ).filter_by(
            marked_by_name=current_user.username
        ).distinct().subquery()
        
        notifications = Notification.query.filter(
            Notification.student_id.in_(marked_student_ids)
        ).order_by(Notification.created_at.desc())\
        .limit(50).all()
    
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'student_name': n.student.name if n.student else None,
            'student_roll': n.student.roll if n.student else None,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for n in notifications],
        'unread_count': unread_count
    })


@app.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@teacher_required
def api_mark_notification_read(notif_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notif_id)
    
    # Check permission
    if not current_user.is_admin() and notification.student_id:
        # Check if teacher marked this student
        marked = Attendance.query.filter_by(
            student_id=notification.student_id,
            marked_by_name=current_user.username
        ).first()
        if not marked:
            return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/notifications/read-all', methods=['POST'])
@teacher_required
def api_mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    user_id = current_user.id
    
    if current_user.is_admin():
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    else:
        # Only mark notifications for students this teacher has marked
        marked_student_ids = db.session.query(
            Attendance.student_id
        ).filter_by(
            marked_by_name=current_user.username
        ).distinct().subquery()
        
        Notification.query.filter(
            Notification.student_id.in_(marked_student_ids),
            Notification.is_read == False
        ).update({'is_read': True}, synchronize_session=False)
    
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/check-low-attendance', methods=['POST'])
@admin_required
def api_check_low_attendance():
    """Manually trigger low attendance check for all students (admin only)"""
    students = Student.query.filter_by(is_trained=True).all()
    alerts_sent = 0
    
    for student in students:
        if check_and_send_low_attendance_alert(student):
            alerts_sent += 1
    
    return jsonify({
        'success': True,
        'students_checked': len(students),
        'alerts_sent': alerts_sent
    })


@admin_required
def api_rectify_attendance():
    """
    Rectify/Correct an attendance record (Admin direct rectification).
    Can change: marked_by, marked_by_name, timestamp, or delete the record.
    
    Expected JSON:
    {
        "attendance_id": 123,
        "action": "update" | "delete",
        "marked_by": 456,  # optional - user ID of teacher
        "marked_by_name": "New Teacher Name",  # optional
        "timestamp": "2026-09-01 10:30:00",  # optional - ISO format
        "reason": "Reason for rectification"  # required
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        attendance_id = data.get('attendance_id')
        action = data.get('action', 'update')
        reason = data.get('reason', '').strip()
        
        if not attendance_id:
            return jsonify({'error': 'Attendance ID required'}), 400
        
        if not reason:
            return jsonify({'error': 'Reason for rectification required'}), 400
        
        attendance = Attendance.query.get_or_404(attendance_id)
        
        if action == 'delete':
            # Store info for notification before deletion
            student = attendance.student
            marked_by_name = attendance.marked_by_name
            timestamp = attendance.timestamp
            
            # Create rectification log notification
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='attendance_rectified',
                    title=f'Attendance Deleted: {student.name}',
                    message=f'Attendance for {student.name} ({student.roll}) on {timestamp.strftime("%Y-%m-%d %H:%M:%S")} was deleted by {current_user.username}. Reason: {reason}'
                )
            
            db.session.delete(attendance)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Attendance record deleted'})
        
        elif action == 'update':
            old_marked_by = attendance.marked_by
            old_marked_by_name = attendance.marked_by_name
            old_timestamp = attendance.timestamp
            
            # Update fields if provided
            if 'marked_by' in data and data['marked_by']:
                new_user = User.query.get(data['marked_by'])
                if not new_user:
                    return jsonify({'error': 'Invalid teacher/user ID'}), 400
                attendance.marked_by = new_user.id
                attendance.marked_by_name = new_user.username
            
            if 'marked_by_name' in data and data['marked_by_name']:
                attendance.marked_by_name = data['marked_by_name']
            
            if 'timestamp' in data and data['timestamp']:
                try:
                    attendance.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
            
            db.session.commit()
            
            # Create rectification log notification
            student = attendance.student
            changes = []
            if old_marked_by != attendance.marked_by:
                changes.append(f"marked_by: {old_marked_by_name} -> {attendance.marked_by_name}")
            if old_timestamp != attendance.timestamp:
                changes.append(f"time: {old_timestamp.strftime('%Y-%m-%d %H:%M:%S')} -> {attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='attendance_rectified',
                    title=f'Attendance Rectified: {student.name}',
                    message=f'Attendance for {student.name} ({student.roll}) rectified by {current_user.username}. Changes: {"; ".join(changes)}. Reason: {reason}'
                )
            
            return jsonify({
                'success': True,
                'message': 'Attendance record updated',
                'attendance': {
                    'id': attendance.id,
                    'student_name': student.name,
                    'student_roll': student.roll,
                    'marked_by_name': attendance.marked_by_name,
                    'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        else:
            return jsonify({'error': 'Invalid action. Use "update" or "delete"'}), 400
            
    except Exception as e:
        print(f"[ERROR] Attendance rectification failed: {e}")
        return jsonify({'error': 'Rectification failed'}), 500


# -----------------------
# API: Direct Attendance Rectification (Admin only)
# -----------------------
@app.route('/api/attendance/rectify', methods=['POST'])
@admin_required
def api_rectify_attendance():
    """
    Direct rectification of attendance by admin (without teacher request).
    Can change: marked_by, marked_by_name, timestamp, or delete the record.
    
    Expected JSON:
    {
        "attendance_id": 123,
        "action": "update" | "delete",
        "marked_by": 456,  # optional - user ID of teacher
        "marked_by_name": "New Teacher Name",  # optional
        "timestamp": "2026-09-01 10:30:00",  # optional - ISO format
        "reason": "Reason for rectification"  # required
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        attendance_id = data.get('attendance_id')
        action = data.get('action', 'update')
        reason = data.get('reason', '').strip()
        
        if not attendance_id:
            return jsonify({'error': 'Attendance ID required'}), 400
        
        if not reason:
            return jsonify({'error': 'Reason for rectification required'}), 400
        
        attendance = Attendance.query.get_or_404(attendance_id)
        
        if action == 'delete':
            student = attendance.student
            timestamp = attendance.timestamp
            
            # Create rectification log notification
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='attendance_rectified',
                    title=f'Attendance Deleted: {student.name}',
                    message=f'Attendance for {student.name} ({student.roll}) on {timestamp.strftime("%Y-%m-%d %H:%M:%S")} was deleted by {current_user.username}. Reason: {reason}'
                )
            
            db.session.delete(attendance)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Attendance record deleted'})
        
        elif action == 'update':
            old_marked_by = attendance.marked_by
            old_marked_by_name = attendance.marked_by_name
            old_timestamp = attendance.timestamp
            
            # Update fields if provided
            if 'marked_by' in data and data['marked_by']:
                new_user = User.query.get(data['marked_by'])
                if not new_user:
                    return jsonify({'error': 'Invalid teacher/user ID'}), 400
                attendance.marked_by = new_user.id
                attendance.marked_by_name = new_user.username
            
            if 'marked_by_name' in data and data['marked_by_name']:
                attendance.marked_by_name = data['marked_by_name']
            
            if 'timestamp' in data and data['timestamp']:
                try:
                    attendance.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
            
            db.session.commit()
            
            # Create rectification log notification
            student = attendance.student
            changes = []
            if old_marked_by != attendance.marked_by:
                changes.append(f"marked_by: {old_marked_by_name} -> {attendance.marked_by_name}")
            if old_timestamp != attendance.timestamp:
                changes.append(f"time: {old_timestamp.strftime('%Y-%m-%d %H:%M:%S')} -> {attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='attendance_rectified',
                    title=f'Attendance Rectified: {student.name}',
                    message=f'Attendance for {student.name} ({student.roll}) rectified by {current_user.username}. Changes: {"; ".join(changes)}. Reason: {reason}'
                )
            
            return jsonify({
                'success': True,
                'message': 'Attendance record updated',
                'attendance': {
                    'id': attendance.id,
                    'student_name': student.name,
                    'student_roll': student.roll,
                    'marked_by_name': attendance.marked_by_name,
                    'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        else:
            return jsonify({'error': 'Invalid action. Use "update" or "delete"'}), 400
            
    except Exception as e:
        print(f"[ERROR] Attendance rectification failed: {e}")
        return jsonify({'error': 'Rectification failed'}), 500


# -----------------------
# Rectification Request Workflow (Teacher -> Admin)
# -----------------------
@app.route('/api/attendance/today-by-student/<int:student_id>', methods=['GET'])
@teacher_required
def api_get_today_attendance_by_student(student_id):
    """Get today's attendance record for a specific student marked by current teacher"""
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        attendance = Attendance.query.filter(
            Attendance.student_id == student_id,
            Attendance.timestamp >= today_start,
            Attendance.marked_by_name == current_user.username
        ).first()
        
        if not attendance:
            return jsonify({'attendance': None})
        
        return jsonify({
            'attendance': {
                'id': attendance.id,
                'student_id': attendance.student_id,
                'marked_by': attendance.marked_by,
                'marked_by_name': attendance.marked_by_name,
                'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        print(f"[ERROR] Get today attendance failed: {e}")
        return jsonify({'error': 'Failed to fetch attendance'}), 500


@app.route('/api/rectification/request', methods=['POST'])
@teacher_required
def api_submit_rectification_request():
    """
    Teacher submits a rectification request for an attendance record.
    
    Expected JSON:
    {
        "attendance_id": 123,
        "requested_marked_by": 456,  # optional - new teacher ID
        "requested_timestamp": "2026-09-01 10:30:00",  # optional - ISO format
        "reason": "Reason for rectification"  # required
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        attendance_id = data.get('attendance_id')
        reason = data.get('reason', '').strip()
        
        if not attendance_id:
            return jsonify({'error': 'Attendance ID required'}), 400
        
        if not reason:
            return jsonify({'error': 'Reason for rectification request required'}), 400
        
        attendance = Attendance.query.get_or_404(attendance_id)
        
        # Check if teacher marked this attendance or has permission
        if attendance.marked_by_name != current_user.username:
            return jsonify({'error': 'You can only request rectification for attendance you marked'}), 403
        
        # Check if request already exists and is pending
        existing = RectificationRequest.query.filter_by(
            attendance_id=attendance_id,
            status='pending'
        ).first()
        if existing:
            return jsonify({'error': 'A pending request already exists for this record'}), 400
        
        # Validate requested changes
        requested_marked_by = data.get('requested_marked_by')
        requested_timestamp = data.get('requested_timestamp')
        
        if requested_marked_by:
            new_teacher = User.query.get(requested_marked_by)
            if not new_teacher or not new_teacher.is_teacher():
                return jsonify({'error': 'Invalid teacher ID'}), 400
        
        if requested_timestamp:
            try:
                requested_timestamp = datetime.fromisoformat(requested_timestamp.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        # Create rectification request
        rect_request = RectificationRequest(
            attendance_id=attendance_id,
            student_id=attendance.student_id,
            teacher_id=current_user.id,
            requested_marked_by=requested_marked_by,
            requested_timestamp=requested_timestamp,
            reason=reason,
            status='pending'
        )
        db.session.add(rect_request)
        db.session.commit()
        
        # Notify admins
        try:
            admins = User.query.filter_by(role='admin').all()
            teacher = current_user
            student = attendance.student
            
            for admin in admins:
                # Create in-app notification
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='rectification_request',
                    title=f'Rectification Request: {student.name}',
                    message=f'{teacher.username} requested rectification for {student.name} ({student.roll}). Reason: {reason}'
                )
                
                # Send email
                send_rectification_request_to_admin(admin, rect_request, teacher, student, attendance)
        except Exception as e:
            print(f"Failed to notify admins: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Rectification request submitted successfully',
            'request_id': rect_request.id
        })
        
    except Exception as e:
        print(f"[ERROR] Submit rectification request failed: {e}")
        return jsonify({'error': 'Failed to submit request'}), 500


@app.route('/api/rectification/pending', methods=['GET'])
@admin_required
def api_get_pending_rectifications():
    """Get all pending rectification requests for admin review"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'pending')
        
        query = RectificationRequest.query.join(Attendance).join(Student).join(User, RectificationRequest.teacher_id == User.id)\
            .order_by(RectificationRequest.created_at.desc())
        
        if status != 'all':
            query = query.filter(RectificationRequest.status == status)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'requests': [{
                'id': r.id,
                'attendance_id': r.attendance_id,
                'student_name': r.student.name,
                'student_roll': r.student.roll,
                'student_uid': r.student.uid,
                'teacher_name': r.teacher.username,
                'teacher_id': r.teacher.teacher_id,
                'current_marked_by': r.attendance.marked_by_name,
                'current_timestamp': r.attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'requested_marked_by': r.new_marked_by.username if r.new_marked_by else None,
                'requested_marked_by_id': r.requested_marked_by,
                'requested_timestamp': r.requested_timestamp.strftime('%Y-%m-%d %H:%M:%S') if r.requested_timestamp else None,
                'reason': r.reason,
                'status': r.status,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'reviewed_at': r.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if r.reviewed_at else None
            } for r in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        print(f"[ERROR] Get pending rectifications failed: {e}")
        return jsonify({'error': 'Failed to fetch requests'}), 500


@app.route('/api/rectification/review', methods=['POST'])
@admin_required
def api_review_rectification_request():
    """
    Admin reviews and decides on a rectification request.
    
    Expected JSON:
    {
        "request_id": 123,
        "action": "approve" | "reject",
        "admin_notes": "Optional notes"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        request_id = data.get('request_id')
        action = data.get('action')
        admin_notes = data.get('admin_notes', '').strip()
        
        if not request_id:
            return jsonify({'error': 'Request ID required'}), 400
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Action must be "approve" or "reject"'}), 400
        
        rect_request = RectificationRequest.query.get_or_404(request_id)
        
        if rect_request.status != 'pending':
            return jsonify({'error': f'Request already {rect_request.status}'}), 400
        
        attendance = rect_request.attendance
        student = rect_request.student
        teacher = rect_request.teacher
        
        if action == 'approve':
            # Approve = mark attendance as absent (delete the attendance record)
            student = rect_request.student
            teacher = rect_request.teacher
            
            # Store attendance info for notification before deletion
            attendance_info = f"{attendance.student.name} ({attendance.student.roll}) on {attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            marked_by = attendance.marked_by_name
            
            # Delete the attendance record (mark as absent)
            db.session.delete(attendance)
            db.session.commit()
            
            # Update request status
            rect_request.status = 'approved'
            rect_request.admin_id = current_user.id
            rect_request.admin_notes = admin_notes
            rect_request.reviewed_at = datetime.now()
            db.session.commit()
            
            # Notify teacher (with error handling)
            try:
                send_rectification_decision_to_teacher(teacher, rect_request, student, current_user, True)
            except Exception as e:
                print(f"Failed to notify teacher: {e}")
            
            # Notify student (with error handling)
            try:
                send_rectification_notification_to_student(student, rect_request, current_user, True)
            except Exception as e:
                print(f"Failed to notify student: {e}")
            
            # Notify admins (with error handling)
            try:
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    create_notification(
                        user_id=admin.id,
                        student_id=student.id,
                        notif_type='attendance_rectified',
                        title=f'Attendance Marked Absent: {student.name}',
                        message=f'Request from {teacher.username} approved by {current_user.username}. Attendance record for {attendance_info} marked as absent (deleted). Reason: {rect_request.reason}'
                    )
            except Exception as e:
                print(f"Failed to notify admins: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Request approved - attendance marked as absent (record deleted)',
                'action': 'deleted'
            })
        
        else:  # reject
            rect_request.status = 'rejected'
            rect_request.admin_id = current_user.id
            rect_request.admin_notes = admin_notes
            rect_request.reviewed_at = datetime.now()
            db.session.commit()
            
            # Notify teacher
            send_rectification_decision_to_teacher(teacher, rect_request, student, current_user, False)
            
            # Notify admins
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    user_id=admin.id,
                    student_id=student.id,
                    notif_type='rectification_rejected',
                    title=f'Rectification Rejected: {student.name}',
                    message=f'Request from {teacher.username} rejected by {current_user.username}. Reason: {rect_request.reason}. Admin notes: {admin_notes}'
                )
            
            return jsonify({
                'success': True,
                'message': 'Request rejected'
            })
            
    except Exception as e:
        print(f"[ERROR] Review rectification request failed: {e}")
        return jsonify({'error': 'Failed to review request'}), 500


@app.route('/api/rectification/my-requests', methods=['GET'])
@teacher_required
def api_get_my_rectification_requests():
    """Get rectification requests submitted by current teacher"""
    try:
        requests = RectificationRequest.query.filter_by(teacher_id=current_user.id)\
            .order_by(RectificationRequest.created_at.desc()).all()
        
        return jsonify({
            'requests': [{
                'id': r.id,
                'attendance_id': r.attendance_id,
                'student_name': r.student.name,
                'student_roll': r.student.roll,
                'current_marked_by': r.attendance.marked_by_name,
                'current_timestamp': r.attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'requested_marked_by': r.new_marked_by.username if r.new_marked_by else None,
                'requested_timestamp': r.requested_timestamp.strftime('%Y-%m-%d %H:%M:%S') if r.requested_timestamp else None,
                'reason': r.reason,
                'status': r.status,
                'admin_notes': r.admin_notes,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'reviewed_at': r.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if r.reviewed_at else None
            } for r in requests]
        })
    except Exception as e:
        print(f"[ERROR] Get my rectification requests failed: {e}")
        return jsonify({'error': 'Failed to fetch requests'}), 500


# -----------------------
# API: Export Attendance to CSV
# -----------------------
    """Get all attendance records with pagination and filters (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    student_id = request.args.get('student_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    marked_by = request.args.get('marked_by')
    
    query = Attendance.query.join(Student).order_by(Attendance.timestamp.desc())
    
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    if date_from:
        try:
            query = query.filter(Attendance.timestamp >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    
    if date_to:
        try:
            query = query.filter(Attendance.timestamp <= datetime.fromisoformat(date_to))
        except ValueError:
            pass
    
    if marked_by:
        query = query.filter(Attendance.marked_by_name == marked_by)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'records': [{
            'id': a.id,
            'student_id': a.student_id,
            'student_name': a.student.name,
            'student_roll': a.student.roll,
            'student_uid': a.student.uid,
            'marked_by': a.marked_by,
            'marked_by_name': a.marked_by_name,
            'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'date': a.timestamp.strftime('%Y-%m-%d'),
            'time': a.timestamp.strftime('%H:%M:%S')
        } for a in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@app.route('/api/teachers/list')
@teacher_required
def api_teachers_list():
    """Get list of all teachers for dropdowns"""
    teachers = User.query.filter_by(role='teacher', is_active=True).all()
    return jsonify({
        'teachers': [{
            'id': t.id,
            'username': t.username,
            'teacher_id': t.teacher_id,
            'email': t.email
        } for t in teachers]
    })


# -----------------------
# API: Export Attendance to CSV
# -----------------------
@app.route('/admin/attendance/export')
@admin_required
def admin_attendance_export():
    """Export attendance records to CSV (admin page)"""
    attendance_records = Attendance.query.join(Student).order_by(Attendance.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Student Roll', 'Student Name', 'Student UID', 'Marked By', 'Timestamp', 'Date', 'Time'])

    for record in attendance_records:
        writer.writerow([
            record.id,
            record.student.roll if record.student else 'N/A',
            record.student.name if record.student else 'N/A',
            record.student.uid if record.student else 'N/A',
            record.marked_by_name or 'Self',
            record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            record.timestamp.strftime('%Y-%m-%d'),
            record.timestamp.strftime('%H:%M:%S')
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


@app.route('/api/export/csv')
def export_csv():
    """Export attendance records to CSV (API)"""
    # TODO: Add pagination for large datasets
    attendance_records = Attendance.query.order_by(Attendance.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Student Roll', 'Student Name', 'Timestamp', 'Date', 'Time'])

    for record in attendance_records:
        writer.writerow([
            record.id,
            record.student.roll if record.student else 'N/A',
            record.student.name if record.student else 'N/A',
            record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            record.timestamp.strftime('%Y-%m-%d'),
            record.timestamp.strftime('%H:%M')
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


# -----------------------
# API: Delete Student
# -----------------------
@app.route('/api/student/<int:student_id>/delete', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student and their attendance records"""
    try:
        student = Student.query.get_or_404(student_id)

        # Delete attendance records first (cascade)
        Attendance.query.filter_by(student_id=student_id).delete()

        # Delete student
        db.session.delete(student)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Student deleted successfully'})
    except Exception as e:
        db.session.rollback()
        # TODO: Log error properly instead of printing
        return jsonify({'success': False, 'error': str(e)}), 500


# -----------------------
# API: Attendance Report
# -----------------------
@app.route('/api/attendance/report')
def attendance_report():
    """Get attendance report with filters"""
    # TODO: Add more filter options (date range, specific student)
    days = request.args.get('days', 7, type=int)
    date_from = datetime.now() - timedelta(days=days)

    records = Attendance.query.filter(Attendance.timestamp >= date_from).all()

    # Group by date
    report = {}
    for record in records:
        date_key = record.timestamp.strftime('%Y-%m-%d')
        if date_key not in report:
            report[date_key] = {'count': 0, 'students': []}
        report[date_key]['count'] += 1
        if record.student:
            report[date_key]['students'].append({
                'roll': record.student.roll,
                'name': record.student.name
            })

    return jsonify({'report': report, 'total': len(records)})


# ========================================
# ATTENDANCE PERCENTAGE & SEARCH (Teacher & Admin)
# ========================================

@app.route('/attendance/students')
@teacher_required
def attendance_students():
    """View all students with attendance percentage"""
    # Get search query
    search = request.args.get('search', '').strip()
    
    # Check if user is teacher or admin
    is_admin = current_user.is_admin()
    
    # For teachers, get only students they have marked attendance for
    if not is_admin:
        # Get distinct students that this teacher has marked attendance for
        marked_student_ids = db.session.query(
            Attendance.student_id
        ).filter_by(
            marked_by_name=current_user.username
        ).distinct().subquery()
        
        # Filter students to only those the teacher has marked
        if search:
            students = Student.query.filter(
                Student.id.in_(marked_student_ids),
                db.or_(
                    Student.name.ilike(f'%{search}%'),
                    Student.roll.ilike(f'%{search}%'),
                    Student.uid.ilike(f'%{search}%')
                )
            ).order_by(Student.name).all()
        else:
            students = Student.query.filter(
                Student.id.in_(marked_student_ids)
            ).order_by(Student.name).all()
    else:
        # Admin sees all students
        if search:
            students = Student.query.filter(
                db.or_(
                    Student.name.ilike(f'%{search}%'),
                    Student.roll.ilike(f'%{search}%'),
                    Student.uid.ilike(f'%{search}%')
                )
            ).order_by(Student.name).all()
        else:
            students = Student.query.order_by(Student.name).all()
    
    # Calculate attendance percentage for each student
    student_attendance = []
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for student in students:
        # For teachers, only count attendance marked by them
        # Admins can see all attendance
        if is_admin:
            # Admin sees all attendance
            total_attendance = db.session.query(db.func.count(db.func.distinct(
                db.func.date(Attendance.timestamp)
            ))).filter_by(student_id=student.id).scalar() or 0
            
            # Get today's attendance with marked_by info
            today_attendance = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.timestamp >= today_start
            ).first()
        else:
            # Teacher only sees attendance they marked
            total_attendance = db.session.query(db.func.count(db.func.distinct(
                db.func.date(Attendance.timestamp)
            ))).filter_by(
                student_id=student.id,
                marked_by_name=current_user.username
            ).scalar() or 0
            
            # Get today's attendance marked by this teacher
            today_attendance = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.timestamp >= today_start,
                Attendance.marked_by_name == current_user.username
            ).first()
        
        # Calculate percentage (based on last 30 days or total working days)
        # For simplicity, using last 30 days as baseline
        days_in_period = 30
        attendance_percentage = (total_attendance / days_in_period * 100) if days_in_period > 0 else 0
        attendance_percentage = min(100, attendance_percentage)  # Cap at 100%
        
        student_attendance.append({
            'student': student,
            'total_attendance': total_attendance,
            'attendance_percentage': round(attendance_percentage, 1),
            'marked_today': bool(today_attendance),
            'marked_by_name': today_attendance.marked_by_name if today_attendance else None
        })
    
    return render_template('attendance_students.html',
                         student_attendance=student_attendance,
                         search_query=search,
                         total_students=len(students),
                         is_admin=is_admin)


# ========================================
# ADMIN USER MANAGEMENT
# ========================================

@app.route('/admin/students')
@admin_required
def admin_students():
    """Admin panel - Manage students and training"""
    students = Student.query.order_by(Student.added_on.desc()).all()

    # Count images in dataset
    import os
    dataset_dir = os.path.join(BASE_DIR, 'dataset')
    files = []
    if os.path.exists(dataset_dir):
        files = os.listdir(dataset_dir)

    image_counts = {
        student.id: sum(file.startswith(f'{student.roll}_') for file in files)
        for student in students
    }
    trained_students = sum(student.is_trained for student in students)

    return render_template(
        'students.html',
        students=students,
        image_counts=image_counts,
        trained_students=trained_students,
    )


# ========================================
# ADMIN TEACHER MANAGEMENT
# ========================================

def generate_teacher_id():
    """
    Generate a unique teacher ID.
    Format: TF followed by 3-digit sequential number (e.g., TF001, TF002)
    """
    # Get the last teacher by ID to find the next sequence number
    last_teacher = User.query.filter_by(role='teacher').order_by(User.id.desc()).first()
    
    if last_teacher and last_teacher.teacher_id and last_teacher.teacher_id.startswith('TF'):
        # Extract the numeric part from the last teacher ID
        try:
            last_number = int(last_teacher.teacher_id[2:])  # Get digits after 'TF'
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        # First teacher with new format or no teachers yet
        next_number = 1
    
    # Format as TF followed by 3-digit zero-padded number
    return f"TF{next_number:03d}"


@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@admin_required
def admin_add_teacher():
    """Admin panel - Add new teacher"""
    import secrets
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validation
        if not username:
            return render_template('add_teacher.html', error='Username is required')

        if not email:
            return render_template('add_teacher.html', error='Email is required')

        # Check if username exists
        if User.query.filter_by(username=username).first():
            return render_template('add_teacher.html', error='Username already taken')

        # Check if email exists
        if User.query.filter_by(email=email).first():
            return render_template('add_teacher.html', error='Email already registered')
        
        # Generate teacher ID and password
        teacher_id = generate_teacher_id()
        
        if not password:
            password = secrets.token_urlsafe(8)  # Generate random 8-character password
        
        # Create new teacher
        teacher = User(
            username=username,
            email=email,
            role='teacher',
            teacher_id=teacher_id,
            is_verified=True  # Auto-verify teachers
        )
        teacher.set_password(password)
        db.session.add(teacher)
        db.session.commit()
        
        flash(f'Teacher added successfully! Teacher ID: {teacher_id}', 'success')
        
        # Store credentials in session to show in modal
        session['new_teacher_credentials'] = {
            'teacher_id': teacher_id,
            'username': username,
            'email': email,
            'password': password
        }
        return redirect(url_for('admin_show_teacher_credentials'))

    return render_template('add_teacher.html')


@app.route('/admin/teachers/credentials')
@admin_required
def admin_show_teacher_credentials():
    """Show generated credentials for newly added teacher"""
    credentials = session.pop('new_teacher_credentials', None)
    if not credentials:
        return redirect(url_for('admin_teachers'))

    return render_template('teacher_credentials.html', credentials=credentials)


@app.route('/admin/teachers')
@admin_required
def admin_teachers():
    """Admin panel - Manage teachers"""
    teachers = User.query.filter_by(role='teacher').order_by(User.created_at.desc()).all()
    
    # Get attendance count for each teacher
    teacher_stats = []
    for teacher in teachers:
        # Count total attendance marked by this teacher
        total_marked = Attendance.query.filter_by(marked_by=teacher.id).count()
        
        # Get recent attendance (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_marked = Attendance.query.filter(
            Attendance.marked_by == teacher.id,
            Attendance.timestamp >= thirty_days_ago
        ).count()
        
        teacher_stats.append({
            'teacher': teacher,
            'total_marked': total_marked,
            'recent_marked': recent_marked
        })
    
    return render_template('teachers.html', teacher_stats=teacher_stats)


@app.route('/admin/teachers/<int:teacher_id>/details')
@admin_required
def admin_teacher_details(teacher_id):
    """View detailed attendance records for a specific teacher"""
    teacher = User.query.get_or_404(teacher_id)
    
    if not teacher.is_teacher():
        flash('User is not a teacher.', 'error')
        return redirect(url_for('admin_teachers'))
    
    # Get all attendance marked by this teacher
    attendance_records = Attendance.query.filter_by(marked_by=teacher.id)\
                                        .order_by(Attendance.timestamp.desc())\
                                        .all()
    
    # Get statistics
    total_marked = len(attendance_records)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_marked = Attendance.query.filter(
        Attendance.marked_by == teacher.id,
        Attendance.timestamp >= today_start
    ).count()
    
    # Last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    last_30_days = Attendance.query.filter(
        Attendance.marked_by == teacher.id,
        Attendance.timestamp >= thirty_days_ago
    ).count()
    
    # Group by student
    students_marked = db.session.query(
        Student.id, Student.name, Student.roll,
        db.func.count(Attendance.id).label('count')
    ).join(Attendance, Student.id == Attendance.student_id)\
     .filter(Attendance.marked_by == teacher.id)\
     .group_by(Student.id, Student.name, Student.roll)\
     .order_by(db.func.count(Attendance.id).desc())\
     .all()
    
    return render_template('teacher_details.html',
                         teacher=teacher,
                         attendance_records=attendance_records,
                         total_marked=total_marked,
                         today_marked=today_marked,
                         last_30_days=last_30_days,
                         students_marked=students_marked)


@app.route('/admin/teachers/<int:teacher_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_teacher(teacher_id):
    """Edit teacher details"""
    teacher = User.query.get_or_404(teacher_id)
    
    if not teacher.is_teacher():
        flash('User is not a teacher.', 'error')
        return redirect(url_for('admin_teachers'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        
        if not username:
            flash('Username is required.', 'error')
            return render_template('edit_teacher.html', teacher=teacher)

        # Check if username is taken by another user
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != teacher.id:
            flash('Username already taken.', 'error')
            return render_template('edit_teacher.html', teacher=teacher)
        
        # Update details
        teacher.username = username
        teacher.email = email
        
        if new_password:
            teacher.set_password(new_password)
            flash('Teacher details updated with new password.', 'success')
        else:
            flash('Teacher details updated.', 'success')
        
        db.session.commit()
        return redirect(url_for('admin_teachers'))

    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/admin/teachers/<int:teacher_id>/delete', methods=['POST'])
@admin_required
def admin_delete_teacher(teacher_id):
    """Delete teacher account"""
    teacher = User.query.get_or_404(teacher_id)
    
    if not teacher.is_teacher():
        flash('User is not a teacher.', 'error')
        return redirect(url_for('admin_teachers'))
    
    # Don't allow deleting if they have marked attendance
    attendance_count = Attendance.query.filter_by(marked_by=teacher.id).count()
    if attendance_count > 0:
        flash(f'Cannot delete teacher. They have marked {attendance_count} attendance records.', 'error')
        return redirect(url_for('admin_teachers'))
    
    db.session.delete(teacher)
    db.session.commit()
    flash(f'Teacher {teacher.username} has been deleted.', 'success')
    return redirect(url_for('admin_teachers'))


@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    """Delete student account"""
    try:
        student = Student.query.get_or_404(student_id)
        student_name = student.name
        student_roll = student.roll

        # First, delete all attendance records for this student (to avoid foreign key errors)
        Attendance.query.filter_by(student_id=student.id).delete()

        # Delete student's face images from dataset
        import os
        dataset_dir = os.path.join(BASE_DIR, 'dataset')
        if os.path.exists(dataset_dir):
            # Delete all images with this student's roll number prefix
            for file in os.listdir(dataset_dir):
                if student_roll and file.startswith(f'{student_roll}_'):
                    file_path = os.path.join(dataset_dir, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file}: {e}")

        # Delete student record
        db.session.delete(student)
        db.session.commit()

        flash(f'Student {student_name} ({student_roll}) has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting student: {e}")
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('admin_students'))


@app.route('/admin/students/<int:student_id>/delete', methods=['GET'])
@admin_required
def admin_delete_student_get(student_id):
    """Redirect GET requests to student management"""
    flash('Invalid request method. Please use the delete button from the student list.', 'warning')
    return redirect(url_for('admin_students'))


# ========================================
# ADMIN - STUDENT CREDENTIALS EXPORT
# ========================================

@app.route('/admin/credentials')
@admin_required
def admin_credentials():
    """Admin panel - View and export student credentials"""
    students = Student.query.order_by(Student.added_on.desc()).all()
    return render_template(
        'credentials_list.html',
        students=students,
        credentials_sent_count=sum(student.credentials_sent for student in students),
        trained_students_count=sum(student.is_trained for student in students),
        pending_credentials_count=sum(not student.credentials_sent for student in students),
    )


@app.route('/admin/credentials/export')
@admin_required
def admin_export_credentials():
    """Export student credentials as CSV file"""
    from flask import send_file
    import csv
    import io

    # Get all students
    students = Student.query.order_by(Student.added_on.desc()).all()

    # Create CSV file in memory
    output = io.StringIO()
    fieldnames = [
        'Name', 'Roll Number', 'Student UID', 'Generated Password', 'Email',
        'Added On', 'Credentials Sent', 'Password Changed', 'Trained'
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    for student in students:
        writer.writerow({
            'Name': student.name,
            'Roll Number': student.roll,
            'Student UID': student.uid,
            # Export the original generated password, not the student's current
            # password hash or a password they chose after first login.
            'Generated Password': student.temporary_password or 'Unavailable (legacy student)',
            'Email': student.email or 'N/A',
            'Added On': student.added_on.strftime('%Y-%m-%d %H:%M:%S') if student.added_on else 'N/A',
            'Credentials Sent': 'Yes' if student.credentials_sent else 'No',
            'Password Changed': 'Yes' if student.password_changed_at else 'No',
            'Trained': 'Yes' if student.is_trained else 'No'
        })

    output.seek(0)

    # Create response with CSV file
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'student_credentials_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin panel - Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)


@app.route('/admin/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def admin_activate_user(user_id):
    """Activate or deactivate user account"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete user account"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin():
        flash('Cannot delete admin user.', 'error')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@admin_required
def admin_change_role(user_id):
    """Change user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['admin', 'teacher', 'student']:
        flash('Invalid role.', 'error')
        return redirect(url_for('admin_users'))
    
    user.role = new_role
    db.session.commit()
    flash(f'User {user.username} role changed to {new_role}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/stats')
@admin_required
def admin_stats():
    """Admin statistics"""
    total_users = User.query.count()
    total_admins = User.query.filter_by(role='admin').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    # Get actual registered students from Student table (not User table)
    total_students = Student.query.count()
    verified_users = User.query.filter_by(is_verified=True).count()

    return jsonify({
        'total_users': total_users,
        'total_admins': total_admins,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'verified_users': verified_users
    })


# -----------------------
# MAIN ENTRY
# -----------------------
if __name__ == '__main__':
    # For production (Render/Railway), use environment PORT
    # For local dev, default to 8000
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    # NOTE: Don't run with debug=True in production - security risk
    app.run(host='0.0.0.0', port=port, debug=debug)
