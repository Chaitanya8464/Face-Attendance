# Student Authentication Enhancements

## Overview

This document describes the enhanced student authentication system with UID/password generation, password management, and profile features.

## Features Added

### 1. **Automatic UID & Password Generation**
When an admin registers a new student:
- **UID**: Auto-generated UUID (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Password**: Random 8-character secure token
- **Email Option**: Admin can optionally provide student email for credential delivery

### 2. **First-Login Password Change Enforcement**
- Students are **required** to change their temporary password on first login
- Password must be at least 6 characters
- System tracks when password was last changed

### 3. **Password Management**
Students can:
- **Change Password**: Update password from profile/dashboard
- **Forgot Password**: Reset password via email verification
- **Security**: Password reset tokens expire after 1 hour

### 4. **Student Profile Management**
Students can:
- View their profile details (UID, Roll, Name, Email)
- Update their name and email
- View registration date and password change history
- Access all account management features from a dropdown menu

### 5. **Email Notifications**
Automated emails for:
- **Credentials**: Sent when admin registers student (if email provided)
- **Password Reset**: Sent when student requests password reset

## Routes Added

### Student Authentication
```
/student-login              - Student login with UID and password
/student-logout             - Student logout
/student/change-password    - Change password (forced on first login)
/student/forgot-password    - Request password reset
/student/reset-password/<token> - Reset password with token
/student/profile            - View and edit profile
/student-dashboard          - Student dashboard
```

## Database Changes

### New Columns in `student` Table
Run the migration script to add these columns:
```bash
python migrate_db_v4.py
```

**Columns Added:**
- `email` (VARCHAR 120, unique, nullable) - Student email
- `first_login` (BOOLEAN, default=True) - First login flag
- `password_changed_at` (DATETIME, nullable) - Last password change timestamp
- `credentials_sent` (BOOLEAN, default=False) - Email sent tracking

## Usage Guide

### For Administrators

#### Registering a Student

1. Navigate to `/register` (Admin only)
2. Fill in the form:
   - **Full Name**: Student's complete name
   - **Roll Number**: Unique identifier (used for face recognition)
   - **Email** (Optional): For sending credentials
3. Click "Proceed to Capture"
4. **Save the generated credentials**:
   - UID (auto-generated)
   - Temporary Password (auto-generated)
5. Share credentials with the student
6. Capture face images for the student

#### Best Practices
- ✅ Always collect student email for secure credential delivery
- ✅ Save credentials in a secure location
- ✅ Inform students to change password on first login
- ✅ Remind students not to share their credentials

### For Students

#### First-Time Login

1. Go to `/student-login`
2. Enter UID and temporary password provided by admin
3. **You will be redirected to change password page**
4. Enter current (temporary) password
5. Create a new strong password (min 6 characters)
6. Confirm new password
7. Click "Change Password"
8. You will be redirected to your dashboard

#### Changing Password

1. Click on **Profile** dropdown (top-right)
2. Select **Change Password**
3. Enter current password
4. Enter new password (min 6 characters)
5. Confirm new password
6. Click "Change Password"

#### Resetting Forgotten Password

1. Go to `/student-login`
2. Click **Forgot Password?**
3. Enter your UID and registered email
4. Check email for reset link
5. Click the reset link (valid for 1 hour)
6. Enter new password and confirm
7. Click "Reset Password"
8. Login with new password

#### Updating Profile

1. Click on **Profile** dropdown (top-right)
2. Select **My Profile**
3. Update name or email as needed
4. Click "Save Changes"

## Security Features

### Password Requirements
- Minimum 6 characters
- Must be different from current password
- Stored as hashed values (never plain text)
- Password change timestamp tracked

### Token Security
- Password reset tokens expire after 1 hour
- Tokens are single-use only
- Tokens are cryptographically secure

### Session Management
- Students can be "Remembered" via cookies
- Sessions can be cleared via logout
- First-login state tracked in database

## Email Configuration

To enable email notifications, configure these environment variables:

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@faceattendance.com
```

### Gmail Setup (Example)
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use App Password in `MAIL_PASSWORD`

## File Structure

```
templates/
├── auth/
│   └── student_login.html          - Student login page
├── student/
│   ├── dashboard.html              - Student dashboard
│   ├── change_password.html        - Change password page
│   ├── forgot_password.html        - Forgot password request
│   ├── reset_password.html         - Password reset with token
│   └── profile.html                - Student profile page
├── admin/
│   └── credentials.html            - Show generated credentials
└── emails/
    ├── student_credentials.html    - Email template for credentials
    └── student_reset_password.html - Email template for password reset
```

## API Endpoints

No new API endpoints added. All features use traditional form submissions.

## Testing Checklist

- [ ] Admin can register student with email
- [ ] Credentials are generated and displayed
- [ ] Email is sent with credentials (if configured)
- [ ] Student can login with UID and password
- [ ] First-time login forces password change
- [ ] Student can change password from profile
- [ ] Forgot password flow works correctly
- [ ] Password reset token expires after 1 hour
- [ ] Student can update profile information
- [ ] Profile dropdown shows all options
- [ ] Logout clears student session

## Troubleshooting

### Issue: Email not sending
**Solution**: Check email configuration in `.env` file. Verify SMTP credentials.

### Issue: First login not detected
**Solution**: Run migration script: `python migrate_db_v4.py`

### Issue: Password change fails
**Solution**: Ensure password meets minimum length requirement (6 characters)

### Issue: Reset link expired
**Solution**: Request a new password reset from the forgot password page

## Migration from Previous Version

If you have existing students:

1. **Backup your database**:
   ```bash
   cp database.db database.db.backup
   ```

2. **Run migration**:
   ```bash
   python migrate_db_v4.py
   ```

3. **Existing students** will have:
   - `first_login` set to `False` (already logged in before)
   - Can still login with existing credentials
   - Can use password reset if they forget password

## Future Enhancements

Potential improvements:
- [ ] Password strength requirements (special chars, numbers)
- [ ] Two-factor authentication (2FA)
- [ ] Password history (prevent reuse)
- [ ] Account lockout after failed attempts
- [ ] Email verification for students
- [ ] Bulk student registration via CSV
- [ ] Student self-registration with admin approval

## Support

For issues or questions, please refer to the main README.md or contact the system administrator.
