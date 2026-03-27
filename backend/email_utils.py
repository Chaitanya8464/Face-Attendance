"""
Email Utilities for Face Attendance System

Provides:
    - Email verification
    - Password reset emails
    - Welcome emails
    
Configuration required in app.py:
    - MAIL_SERVER
    - MAIL_PORT
    - MAIL_USE_TLS
    - MAIL_USERNAME
    - MAIL_PASSWORD
    - MAIL_DEFAULT_SENDER
"""
from flask import render_template, url_for, current_app
from flask_mail import Mail, Message
from threading import Thread

# Initialize Flask-Mail
mail = Mail()


def send_async_email(app, msg):
    """Send email asynchronously to avoid blocking"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")


def send_email(subject, recipients, text_body, html_body):
    """Send email with both text and HTML body"""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send in background thread
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_verification_email(user):
    """
    Send email verification link to user.
    
    Args:
        user: User object to verify
    """
    # Generate verification token (in production, use secure token)
    from itsdangerous import URLSafeTimedSerializer
    
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='email-verification')
    
    verify_url = url_for('verify_email_token', token=token, _external=True)
    
    subject = 'Verify Your Email - Face Attendance System'
    
    text_body = f'''
Hello {user.username},

Welcome to Face Attendance System!

Please click the link below to verify your email address:
{verify_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
Face Attendance System Team
'''
    
    html_body = render_template(
        'verify_email.html',
        username=user.username,
        verify_url=verify_url
    )
    
    return send_email(subject, [user.email], text_body, html_body)


def send_password_reset_email(user):
    """
    Send password reset link to user.
    
    Args:
        user: User object requesting password reset
    """
    token = user.generate_reset_token()
    db.session.commit()
    
    reset_url = url_for('reset_password', token=token, _external=True)
    
    subject = 'Password Reset - Face Attendance System'
    
    text_body = f'''
Hello {user.username},

You requested a password reset for your account.

Please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
Face Attendance System Team
'''
    
    html_body = render_template(
        'reset_password.html',
        username=user.username,
        reset_url=reset_url
    )
    
    return send_email(subject, [user.email], text_body, html_body)


def send_welcome_email(user):
    """
    Send welcome email to newly registered user.

    Args:
        user: New user object
    """
    subject = 'Welcome to Face Attendance System!'

    login_url = url_for('login', _external=True)

    text_body = f'''
Hello {user.username},

Welcome to Face Attendance System!

Your account has been created successfully.
Username: {user.username}
Email: {user.email}
Role: {user.role.capitalize()}

You can now log in at:
{login_url}

Best regards,
Face Attendance System Team
'''

    html_body = render_template(
        'welcome.html',
        username=user.username,
        login_url=login_url,
        role=user.role.capitalize()
    )

    return send_email(subject, [user.email], text_body, html_body)


def send_student_credentials_email(student, password):
    """
    Send login credentials to student.

    Args:
        student: Student object
        password: Plain text password (temporary)
    """
    if not student.email:
        return None

    student_login_url = url_for('student_login', _external=True)

    subject = 'Your Login Credentials - Face Attendance System'

    text_body = f'''
Hello {student.name},

Welcome to Face Attendance System!

Your student account has been created. Please use the following credentials to log in:

Student UID: {student.uid}
Roll Number: {student.roll}
Temporary Password: {password}

You can log in at:
{student_login_url}

IMPORTANT:
- You will be required to change your password on first login
- Please keep your credentials secure
- Do not share your password with anyone

Best regards,
Face Attendance System Team
'''

    html_body = render_template(
        'student_credentials.html',
        student_name=student.name,
        student_uid=student.uid,
        student_roll=student.roll,
        password=password,
        login_url=student_login_url
    )

    return send_email(subject, [student.email], text_body, html_body)


def send_student_password_reset_email(student, token):
    """
    Send password reset link to student.

    Args:
        student: Student object requesting password reset
        token: Reset token
    """
    if not student.email:
        return None

    reset_url = url_for('student_reset_password', token=token, _external=True)

    subject = 'Password Reset - Face Attendance System (Student)'

    text_body = f'''
Hello {student.name},

You requested a password reset for your student account.

Please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
Face Attendance System Team
'''

    html_body = render_template(
        'student_reset_password.html',
        student_name=student.name,
        reset_url=reset_url
    )

    return send_email(subject, [student.email], text_body, html_body)
