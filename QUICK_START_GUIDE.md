# Quick Start Guide - Student Authentication System

## For Administrators

### 🎓 Registering a New Student

**Step 1: Go to Registration Page**
- Navigate to: `/register`
- Or click "Register" in the navigation menu

**Step 2: Fill Student Details**
```
✓ Full Name: Enter complete name
✓ Roll Number: Unique ID (letters + numbers only)
✓ Email (Optional): For sending credentials
```

**Step 3: Save Generated Credentials**
```
⚠️ IMPORTANT: Save these credentials securely!

UID: 550e8400-e29b-41d4-a716-446655440000 (example)
Password: abc123xyz (temporary)
```

**Step 4: Share with Student**
- Send UID and password to student
- Or email is sent automatically (if email provided)

**Step 5: Capture Face Images**
- Click "Capture Face Images"
- Take 3-5 photos from different angles
- Ensure good lighting and face is visible

---

## For Students

### 🔐 First-Time Login

**Step 1: Go to Student Login**
- Navigate to: `/student-login`
- Or click "Student Login" on homepage

**Step 2: Enter Credentials**
```
UID: [provided by admin]
Password: [temporary password]
```

**Step 3: Change Password (Required)**
```
✓ Enter current (temporary) password
✓ Create new password (min 6 characters)
✓ Confirm new password
✓ Click "Change Password"
```

**Step 4: Access Dashboard**
- View your attendance records
- Update your profile
- Mark attendance using face recognition

---

### 🔑 Forgot Password?

**Step 1: Request Reset**
- Click "Forgot Password?" on login page
- Enter your UID and registered email

**Step 2: Check Email**
- Look for password reset email
- Click the reset link (valid for 1 hour)

**Step 3: Reset Password**
- Enter new password
- Confirm password
- Click "Reset Password"

**Step 4: Login**
- Use your UID and new password to login

---

### 👤 Update Profile

**Step 1: Open Profile Menu**
- Click "Profile" dropdown (top-right corner)

**Step 2: Select Option**
```
• My Profile - Edit details
• Change Password - Update password
• Logout - Sign out
```

**Step 3: Save Changes**
- Update name or email as needed
- Click "Save Changes"

---

## 📧 Email Setup (For Admins)

To enable automatic credential emails:

**1. Edit `.env` file:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@faceattendance.com
```

**2. Gmail Setup:**
- Enable 2-Factor Authentication
- Generate App Password: https://myaccount.google.com/apppasswords
- Use App Password in `MAIL_PASSWORD`

---

## 🔒 Security Best Practices

### For Admins
✅ Collect student email for secure delivery  
✅ Save credentials in secure location  
✅ Remind students to change password  
✅ Never share passwords in plain text channels  

### For Students
✅ Change password immediately on first login  
✅ Use strong, unique password  
✅ Don't share credentials with classmates  
✅ Logout when using shared computers  

---

## 📱 Quick Links

| Action | URL |
|--------|-----|
| Student Login | `/student-login` |
| Forgot Password | `/student/forgot-password` |
| Student Dashboard | `/student-dashboard` |
| Change Password | `/student/change-password` |
| My Profile | `/student/profile` |
| Admin Register | `/register` |

---

## ❓ FAQ

**Q: Can I change my UID?**  
A: No, UID is permanent and cannot be changed.

**Q: What if I forget my UID?**  
A: Contact your administrator to retrieve your UID.

**Q: How long is the reset link valid?**  
A: Password reset links expire after 1 hour.

**Q: Can I use the same password as before?**  
A: Yes, but it's recommended to use a new unique password.

**Q: Do I need to capture face images again?**  
A: No, face images are separate from login credentials.

---

## 🆘 Need Help?

**Students:** Contact your system administrator  
**Admins:** Check `STUDENT_AUTH_ENHANCEMENTS.md` for detailed docs  

---

**Last Updated:** March 19, 2026  
**Version:** 1.0
