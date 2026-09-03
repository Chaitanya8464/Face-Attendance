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


def send_attendance_notification(student, marked_by_name, marked_at):
    """
    Send notification when attendance is marked for a student.
    
    Args:
        student: Student object
        marked_by_name: Name of teacher/admin who marked attendance
        marked_at: Timestamp when attendance was marked
    """
    if not student.email:
        return None

    subject = f'Attendance Marked - {student.name}'

    text_body = f'''
Hello {student.name},

Your attendance has been marked for today.

Details:
- Student: {student.name} ({student.roll})
- Marked by: {marked_by_name}
- Time: {marked_at.strftime('%Y-%m-%d %H:%M:%S')}

This is an automated notification from Face Attendance System.

Best regards,
Face Attendance System Team
'''

    html_body = render_template(
        'attendance_notification.html',
        student_name=student.name,
        student_roll=student.roll,
        marked_by=marked_by_name,
        marked_at=marked_at
    )

    return send_email(subject, [student.email], text_body, html_body)


def send_low_attendance_notification(student, attendance_percentage, threshold=75):
    """
    Send notification when student attendance falls below threshold.
    
    Args:
        student: Student object
        attendance_percentage: Current attendance percentage
        threshold: Threshold percentage (default 75%)
    """
    if not student.email:
        return None

    subject = f'Low Attendance Alert - {student.name} ({attendance_percentage:.1f}%)'

    text_body = f'''
Hello {student.name},

This is an automated alert regarding your attendance.

Your current attendance percentage is {attendance_percentage:.1f}%, which is below the required threshold of {threshold}%.

Please ensure you attend classes regularly to improve your attendance.

Details:
- Student: {student.name} ({student.roll})
- Current Attendance: {attendance_percentage:.1f}%
- Required Minimum: {threshold}%

If you believe this is an error, please contact your teacher or admin.

Best regards,
Face Attendance System Team
'''

    html_body = render_template(
        'low_attendance_notification.html',
        student_name=student.name,
        student_roll=student.roll,
        attendance_percentage=attendance_percentage,
        threshold=threshold
    )

    return send_email(subject, [student.email], text_body, html_body)


def send_attendance_marked_to_admin(admin_user, student, marked_by_name, marked_at):
    """
    Send notification to admin when attendance is marked.
    
    Args:
        admin_user: Admin User object
        student: Student object
        marked_by_name: Name of teacher/admin who marked attendance
        marked_at: Timestamp when attendance was marked
    """
    if not admin_user.email:
        return None

    subject = f'Attendance Marked: {student.name} by {marked_by_name}'

    text_body = f'''
Hello {admin_user.username},

Attendance has been marked for a student.

Details:
- Student: {student.name} ({student.roll})
- Marked by: {marked_by_name}
- Time: {marked_at.strftime('%Y-%m-%d %H:%M:%S')}

Face Attendance System
'''

    html_body = render_template(
        'attendance_admin_notification.html',
        admin_name=admin_user.username,
        student_name=student.name,
        student_roll=student.roll,
        marked_by=marked_by_name,
        marked_at=marked_at
    )

    return send_email(subject, [admin_user.email], text_body, html_body)


def create_notification(user_id, student_id, notif_type, title, message):
    """
    Create an in-app notification record.
    
    Args:
        user_id: User ID to notify (admin/teacher)
        student_id: Related student ID (optional)
        notif_type: Type of notification
        title: Notification title
        message: Notification message
    """
    from models import db, Notification
    notif = Notification(
        user_id=user_id,
        student_id=student_id,
        type=notif_type,
        title=title,
        message=message
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def send_rectification_request_to_admin(admin_user, request_obj, teacher, student, attendance):
    """
    Send notification to admin when teacher submits rectification request.
    """
    if not admin_user.email:
        return None

    subject = f'Rectification Request: {student.name} by {teacher.username}'

    text_body = f'''
Hello {admin_user.username},

A teacher has submitted a rectification request for attendance.

Details:
- Student: {student.name} ({student.roll})
- Requested by: {teacher.username} ({teacher.teacher_id})
- Current marked by: {attendance.marked_by_name or 'Self'}
- Current time: {attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- Requested change: {get_requested_change_text(request_obj)}
- Reason: {request_obj.reason}

Please review at: /admin/attendance/rectify

Face Attendance System
'''

    html_body = render_template(
        'rectification_admin_notification.html',
        admin_name=admin_user.username,
        student_name=student.name,
        student_roll=student.roll,
        teacher_name=teacher.username,
        teacher_id=teacher.teacher_id,
        current_marked_by=attendance.marked_by_name or 'Self',
        current_time=attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        requested_change=get_requested_change_text(request_obj),
        reason=request_obj.reason,
        request_id=request_obj.id
    )

    return send_email(subject, [admin_user.email], text_body, html_body)


def send_rectification_decision_to_teacher(teacher, request_obj, student, admin, approved):
    """
    Send notification to teacher when admin decides on rectification request.
    """
    if not teacher.email:
        return None

    action = 'approved' if approved else 'rejected'
    subject = f'Rectification Request {action.capitalize()}: {student.name}'

    text_body = f'''
Hello {teacher.username},

Your rectification request has been {action} by {admin.username}.

Details:
- Student: {student.name} ({student.roll})
- Your reason: {request_obj.reason}
- Admin notes: {request_obj.admin_notes or 'None'}

{'The attendance record has been updated accordingly.' if approved else 'The attendance record remains unchanged.'}

Face Attendance System
'''

    html_body = render_template(
        'rectification_teacher_notification.html',
        teacher_name=teacher.username,
        student_name=student.name,
        student_roll=student.roll,
        action=action,
        admin_name=admin.username,
        reason=request_obj.reason,
        admin_notes=request_obj.admin_notes
    )

    return send_email(subject, [teacher.email], text_body, html_body)


def send_rectification_notification_to_student(student, request_obj, admin, approved):
    """
    Send notification to student when their attendance is rectified.
    """
    if not student.email or not approved:
        return None

    subject = f'Attendance Updated: {student.name}'

    text_body = f'''
Hello {student.name},

Your attendance record has been updated by {admin.username}.

Details:
- Student: {student.name} ({student.roll})
- Original marked by: {request_obj.attendance.marked_by_name or 'Self'}
- Updated by: {admin.username}
- Reason: {request_obj.reason}
- Admin notes: {request_obj.admin_notes or 'None'}

Face Attendance System
'''

    html_body = render_template(
        'rectification_student_notification.html',
        student_name=student.name,
        student_roll=student.roll,
        admin_name=admin.username,
        reason=request_obj.reason,
        admin_notes=request_obj.admin_notes
    )

    return send_email(subject, [student.email], text_body, html_body)


def get_requested_change_text(request_obj):
    """Generate human-readable text for requested changes."""
    changes = []
    if request_obj.requested_marked_by:
        new_teacher = request_obj.new_marked_by
        if new_teacher:
            changes.append(f"Marked by: {new_teacher.username} ({new_teacher.teacher_id})")
    if request_obj.requested_timestamp:
        changes.append(f"Time: {request_obj.requested_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    return "; ".join(changes) if changes else "No specific changes requested"
