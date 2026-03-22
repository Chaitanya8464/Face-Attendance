# User Management & Authentication Guide

## 🎯 Overview

The Face Attendance System now includes a complete user management and authentication system with role-based access control.

## 👥 User Roles

### Admin
- **Full system access**
- Manage all users (activate/deactivate/delete)
- Change user roles
- View system statistics
- Access all features

### Teacher
- **Manage students and attendance**
- Register new students
- Capture face images
- Train the recognition model
- Mark and view attendance
- Export attendance reports

### Student
- **View own attendance**
- Mark attendance via face recognition
- View personal attendance records
- Limited dashboard access

## 🚀 Getting Started

### Default Admin Account

After first run, a default admin account is created:

```
Email: admin@faceattendance.com
Password: admin123
```

**⚠️ IMPORTANT:** Change this password immediately in production!

### Registration

1. Go to `/signup` or click "Sign Up" in navigation
2. Fill in:
   - Username (unique)
   - Email (unique)
   - Role (Student or Teacher)
   - Password (min 6 characters)
3. Verify your email (check inbox)
4. Log in with credentials

## 🔐 Authentication Features

### Login/Logout
- **Login Page:** `/login`
- **Logout:** Click username → Logout
- **Remember Me:** Option to stay logged in

### Email Verification
- Verification email sent on signup
- Required for full access
- Resend option available
- Token expires in 24 hours

### Password Recovery
1. Click "Forgot Password?" on login page
2. Enter your email
3. Check email for reset link
4. Enter new password
5. Link expires in 1 hour

## 📧 Email Configuration

To enable email features (verification & password reset), configure these environment variables:

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@faceattendance.com
```

### Gmail Setup
1. Enable 2FA on your Google account
2. Generate an App Password
3. Use the App Password (not your regular password)

### Alternative Email Providers
- **Outlook:** `smtp-mail.outlook.com`, Port 587
- **Yahoo:** `smtp.mail.yahoo.com`, Port 587
- **Custom:** Update MAIL_SERVER accordingly

## 🛡️ Security Features

### Password Security
- Passwords are hashed using Werkzeug (PBKDF2)
- Minimum 6 characters required
- Never stored in plain text

### Session Management
- Secure session cookies
- Remember me functionality
- Automatic logout on inactivity

### Role-Based Access
- Decorators protect routes
- Automatic redirects for unauthorized access
- UI elements hidden based on role

### Token Security
- Secure token generation (URLSafeTimedSerializer)
- Time-limited tokens
- Single-use reset tokens

## 📊 Admin Panel

### Access
- Login as admin
- Click username → Admin → Manage Users
- Or go to `/admin/users`

### User Management

#### View Users
- See all registered users
- Filter by role/status
- View verification status

#### Change Role
- Dropdown in users table
- Instant role change
- Cannot change own role

#### Activate/Deactivate
- Toggle user account status
- Deactivated users cannot log in
- Useful for temporary suspension

#### Delete User
- Permanent deletion
- Cannot delete admin accounts
- Confirmation modal prevents accidents

## 🎨 Role-Based Dashboards

### Admin Dashboard
- User statistics
- Quick action cards
- System overview
- User management access

### Teacher Dashboard
- Student registration
- Attendance marking
- Model training
- Class management

### Student Dashboard
- Mark attendance
- View records
- Attendance tips
- Personal stats

## 🔗 Protected Routes

### Public Routes (No Login Required)
- `/` - Home page
- `/login` - Login page
- `/signup` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password/<token>` - Password reset form
- `/verify-email/<token>` - Email verification

### Teacher/Admin Only
- `/register` - Register student
- `/capture/<roll>` - Capture face images
- `/train` - Train recognition model

### Admin Only
- `/admin/users` - User management
- `/admin/users/<id>/activate` - Toggle user status
- `/admin/users/<id>/delete` - Delete user
- `/admin/users/<id>/role` - Change user role
- `/admin/stats` - System statistics

### All Logged-In Users
- `/dashboard` - Role-specific dashboard
- `/attendance` - Mark attendance
- `/api/*` - API endpoints

## 📝 API Endpoints

### Authentication
```
POST /login          - User login
POST /signup         - User registration
GET  /logout         - User logout
POST /forgot-password - Request password reset
POST /reset-password/<token> - Reset password
GET  /verify-email/<token> - Verify email
```

### Admin
```
GET  /admin/users           - List all users
POST /admin/users/<id>/activate - Toggle user status
POST /admin/users/<id>/delete   - Delete user
POST /admin/users/<id>/role     - Change user role
GET  /admin/stats          - Get statistics
```

## 🐛 Troubleshooting

### Email Not Sending
1. Check email credentials
2. Verify MAIL_PORT is correct
3. Enable "Less secure apps" or use App Password
4. Check firewall/antivirus

### Cannot Access Admin Panel
- Ensure you're logged in as admin
- Check user role in database
- Default admin: `admin@faceattendance.com`

### Password Reset Not Working
- Check email spam folder
- Link expires in 1 hour
- Request new reset link

### Email Verification Issues
- Check spam folder
- Use resend verification option
- Token expires in 24 hours

## 💡 Best Practices

### For Administrators
1. Change default admin password immediately
2. Regularly review user accounts
3. Deactivate instead of deleting when possible
4. Keep email configuration secure

### For Teachers
1. Verify student information before registration
2. Capture multiple face angles for better recognition
3. Retrain model after adding students
4. Export attendance records regularly

### For Students
1. Verify email immediately after signup
2. Use strong, unique password
3. Mark attendance in good lighting
4. Report issues to teacher

## 🔧 Database Schema

### Users Table
```sql
id              INTEGER PRIMARY KEY
email           VARCHAR(120) UNIQUE NOT NULL
username        VARCHAR(80) UNIQUE NOT NULL
password_hash   VARCHAR(255) NOT NULL
role            VARCHAR(20) NOT NULL  -- admin, teacher, student
is_verified     BOOLEAN DEFAULT FALSE
is_active       BOOLEAN DEFAULT TRUE
created_at      DATETIME
last_login      DATETIME
reset_token     VARCHAR(100)
reset_token_expiry DATETIME
```

## 📚 Code Structure

```
attendance-face-recog/
├── app.py                 # Main application + auth routes
├── models.py              # User model + authentication
├── auth_utils.py          # Auth decorators & utilities
├── email_utils.py         # Email sending functions
├── templates/
│   ├── base.html          # Base template with nav
│   ├── auth/
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── verify_email.html
│   │   ├── forgot_password.html
│   │   └── reset_password.html
│   ├── admin/
│   │   └── users.html
│   ├── dashboard_admin.html
│   ├── dashboard_teacher.html
│   └── dashboard_student.html
└── templates/emails/
    ├── verify_email.html
    ├── reset_password.html
    └── welcome.html
```

## 🎓 Quick Start Guide

1. **First Time Setup**
   ```bash
   python app.py
   # Login with default admin credentials
   ```

2. **Create Teacher Account**
   - Go to /signup
   - Register as Teacher
   - Verify email

3. **Register Students**
   - Login as teacher
   - Go to Register page
   - Add student details

4. **Start Using**
   - Capture face images
   - Train model
   - Mark attendance

## 📞 Support

For issues or questions:
- Check this documentation first
- Review error logs in console
- Contact system administrator

---

**Version:** 2.0.0  
**Last Updated:** March 2025
