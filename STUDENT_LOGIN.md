# Student Login & Credentials System

## 🎯 Overview

Students can now login with their unique UID and password to view their personal attendance records with timestamps.

## 🔐 System Flow

### 1. Admin Registers Student
- Admin goes to **Admin → Students**
- Clicks **"Register New Student"**
- Enters name and roll number
- **System automatically generates:**
  - Unique UID (UUID format)
  - Temporary password (8 characters)
- Credentials shown to admin
- Admin shares credentials with student

### 2. Student Logins
- Student goes to **Student Login** (`/student-login`)
- Enters UID and password
- Clicks "Login to Dashboard"
- Redirected to personal dashboard

### 3. Student Views Attendance
- Dashboard shows:
  - Total attendance count
  - Whether marked today
  - Face training status
  - Complete attendance history with dates and times
- Can mark attendance via face recognition

## 📋 Features

### Admin Features

#### Student Registration with Credentials
- **Auto-generated UID**: 36-character UUID
- **Auto-generated Password**: 8-character random password
- **Credentials Display**: Shown immediately after registration
- **Copy to Clipboard**: One-click copy for UID and password

#### Student Management
- View all registered students
- Click on any student to see credentials modal
- Credentials modal shows:
  - Student information (name, roll, UID)
  - Login URL
  - Password (hidden by default, click to reveal)
- Can reset passwords if needed

### Student Features

#### Student Login
- **Login URL**: `/student-login`
- **Credentials**: UID + Password
- **Remember Me**: Option to stay logged in
- **Error Handling**: Clear error messages

#### Student Dashboard
- **Personal Information**:
  - Name
  - Roll number
  - UID (partial display)
- **Attendance Statistics**:
  - Total attendance count
  - Marked today status (Yes/No)
  - Face training status
- **Attendance Records Table**:
  - Date (YYYY-MM-DD)
  - Time (HH:MM:SS)
  - Day of week
  - Sequential numbering
- **Quick Actions**:
  - Mark attendance (go to attendance page)
  - View personal status

## 🔧 Technical Implementation

### Database Schema

```sql
-- Student table updates
password_hash VARCHAR(255)  -- Hashed password for login
```

### Password Security

- Passwords are hashed using Werkzeug (PBKDF2)
- Never stored in plain text
- Minimum 8 characters (auto-generated)
- Students can request admin to change password

### Session Management

- Students have separate login session
- Session stored in Flask session
- Logout clears session data
- Timeout after browser close (unless "Remember Me" selected)

### Routes

```python
# Student Authentication
GET  /student-login          # Student login page
POST /student-login          # Process student login
GET  /student-dashboard      # Student dashboard (protected)
GET  /student-logout         # Student logout

# Admin Credentials Management
GET  /show-credentials       # Show credentials after registration
GET  /admin/students         # View all students with credentials modal
```

## 📸 Screenshots

### Student Login Page
```
URL: /student-login
- UID input field
- Password input field
- Remember me checkbox
- Login button
- Info message about credentials
```

### Student Dashboard
```
Shows:
- Student name and roll
- UID (first 8 characters)
- 3 stat cards (Total, Today, Trained)
- Attendance records table
- Quick action cards
```

### Admin Credentials Modal
```
When clicking key icon on student:
- Student info card (name, roll, UID)
- Login credentials card
  - Login URL (copyable)
  - Password (hidden/reveal toggle)
- Close button
- Register new student button
```

## 🎨 UI/UX Features

### Credentials Display
- **Success gradient background** for registration success
- **Copy buttons** for UID and password
- **Visual feedback** when copying (icon changes)
- **Clear instructions** for admin

### Student Dashboard
- **Clean, simple layout** focused on attendance
- **Color-coded badges** for status
- **Responsive table** for attendance records
- **Empty state** with call-to-action if no records

### Security Features
- **Password hashing** (Werkzeug PBKDF2)
- **Session-based authentication**
- **Protected routes** (redirect if not logged in)
- **Auto-logout** on session expiry

## 📝 Workflow Example

### Complete Flow

```
┌─────────────────────────────────────────┐
│ ADMIN REGISTERS STUDENT                 │
│                                         │
│ 1. Admin clicks "Register New Student" │
│ 2. Enters: Name, Roll Number           │
│ 3. System generates:                   │
│    - UID: a7824414-f025-63d3-...       │
│    - Password: xK9mP2nQ                │
│ 4. Credentials shown to admin          │
│ 5. Admin shares with student           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ STUDENT LOGINS                          │
│                                         │
│ 1. Student goes to /student-login      │
│ 2. Enters UID and password             │
│ 3. Clicks "Login to Dashboard"         │
│ 4. Redirected to personal dashboard    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ STUDENT VIEWS ATTENDANCE                │
│                                         │
│ 1. Dashboard shows:                    │
│    - Total: 45 attendances             │
│    - Today: Yes                        │
│    - Trained: Yes                      │
│ 2. Table shows all records with:       │
│    - Date: 2025-03-18                  │
│    - Time: 09:15:23                    │
│    - Day: Tuesday                      │
│ 3. Can mark new attendance             │
└─────────────────────────────────────────┘
```

## 🔐 Security Considerations

### Password Management
- ✅ Passwords are hashed before storage
- ✅ Minimum 8 characters (auto-generated)
- ✅ Use secure random generation
- ⚠️ Students cannot change password themselves (contact admin)
- ⚠️ Consider adding password reset feature

### Session Security
- ✅ Session-based authentication
- ✅ Protected routes redirect if not logged in
- ✅ Logout clears session data
- ⚠️ Consider adding session timeout
- ⚠️ Consider adding "Remember Me" token rotation

### UID Security
- ✅ UUID format (hard to guess)
- ✅ Unique constraint in database
- ✅ Indexed for fast lookup
- ✅ Cannot be changed once generated

## 🐛 Troubleshooting

### Student Cannot Login

**Problem:** "Invalid UID or password"

**Solutions:**
1. Verify UID is correct (check for typos)
2. Check password is correct (case-sensitive)
3. Contact admin to verify credentials
4. Admin can view credentials in student management

### Credentials Not Showing

**Problem:** Admin can't see student password

**Solutions:**
1. Click the key icon next to student name
2. Modal should show credentials
3. If modal doesn't appear, refresh page
4. Check browser console for JavaScript errors

### Student Dashboard Not Loading

**Problem:** Redirected to login page

**Solutions:**
1. Session may have expired
2. Login again with UID and password
3. Check "Remember Me" for longer sessions
4. Clear browser cache and cookies

## 📚 API Endpoints

### Student Authentication

```
GET  /student-login              # Login page
POST /student-login              # Authenticate student
     - uid: Student UID
     - password: Student password
     - remember: Boolean (optional)

GET  /student-dashboard          # View attendance (protected)
GET  /student-logout             # Logout student
```

### Admin Credentials

```
GET  /show-credentials           # Show credentials after registration
GET  /admin/students             # View all students
POST /admin/students/:id/credentials  # View/reset credentials (future)
```

## 🎓 Best Practices

### For Admins

1. ✅ **Save credentials securely** - Store in password manager
2. ✅ **Share securely** - Don't send via plain text email
3. ✅ **Verify student received** - Confirm student can login
4. ✅ **Monitor usage** - Check dashboard for unusual activity
5. ✅ **Reset if compromised** - Contact system admin if needed

### For Students

1. ✅ **Save credentials** - Write down or save in password manager
2. ✅ **Don't share** - Keep UID and password private
3. ✅ **Request change** - Ask admin to change password if needed
4. ✅ **Logout on shared devices** - Always logout after use
5. ✅ **Report issues** - Contact admin if can't access dashboard

## 📊 Future Enhancements

### Planned Features
- [ ] Student password change (self-service)
- [ ] Password reset via email
- [ ] Profile picture upload
- [ ] Attendance statistics charts
- [ ] Download attendance report (PDF)
- [ ] Mobile app for students
- [ ] Push notifications for attendance
- [ ] Attendance percentage calculation

### Security Improvements
- [ ] Two-factor authentication
- [ ] Session timeout settings
- [ ] Login attempt limiting
- [ ] Password strength requirements
- [ ] Audit log for logins

---

**Version:** 2.2.0  
**Last Updated:** March 2025  
**Author:** Face Attendance System Team
