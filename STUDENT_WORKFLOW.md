# Student Registration & Training Workflow

## 🎯 Overview

The system now implements a secure, admin-controlled student registration and training workflow:

1. **Admin registers** student → Unique UID generated
2. **Admin captures** student's face images
3. **Admin trains** the face recognition model
4. **Students mark attendance** using their trained faces

## 🔐 Access Control

### Admin Only
- ✅ Register new students
- ✅ Capture face images
- ✅ Train face recognition model
- ✅ View all students and training status
- ✅ Manage user accounts

### Teachers
- ✅ Mark attendance (view only)
- ✅ View attendance records
- ❌ Cannot register students
- ❌ Cannot train model

### Students
- ✅ Mark attendance (via face recognition)
- ✅ View own attendance
- ❌ Cannot register other students
- ❌ Cannot access admin features

## 📋 Registration Process

### Step 1: Admin Registration

1. Login as admin
2. Go to **Admin → Students** or `/admin/students`
3. Click **"Register New Student"**
4. Fill in:
   - **Full Name**: Student's complete name
   - **Roll Number**: Unique identifier (e.g., CS2024001)
5. **System automatically generates** a unique UID (UUID format)
6. Student is created with status: **"Pending Training"**

**Example UID:** `a7824414-f025-63d3-9c4e-1234567890ab`

### Step 2: Face Capture

1. After registration, you're redirected to capture page
2. Allow camera access
3. Capture **5-10 images** from different angles:
   - Front view
   - Slight left turn
   - Slight right turn
   - Looking up slightly
   - Looking down slightly
4. Ensure good lighting
5. Click **"Save & Train"** when done

### Step 3: Train Model

1. Go to **Train** page or `/train`
2. Click **"Train Model"**
3. System processes all captured images
4. Generates 128-dimensional face encodings
5. Marks student as **"Trained"**
6. Student can now mark attendance!

## 🎓 Student Attendance Process

### For Students (After Training)

1. Go to **Attendance** page or `/attendance`
2. Allow camera access
3. Face the camera
4. System recognizes trained face
5. Attendance marked automatically
6. **One attendance per day** per student

### Important Notes

- ⚠️ **Only trained students** can mark attendance
- ⚠️ Untrained students will be ignored by the system
- ⚠️ Each student can mark attendance **once per day**
- ⚠️ Good lighting required for accurate recognition

## 📊 Admin Dashboard Features

### Student Management Page (`/admin/students`)

View all students with:
- **UID** (first 8 characters shown)
- **Name**
- **Roll Number**
- **Number of captured images**
- **Training Status** (Trained/Pending)
- **Training Date**
- **Registration Date**
- **Quick Actions** (Capture, View Attendance)

### Statistics Cards

- **Total Students**: All registered students
- **Trained**: Students ready to mark attendance
- **Pending Training**: Need face capture/training
- **Train All**: Quick link to train model

## 🔧 Technical Details

### Database Schema Updates

```sql
-- New columns added to student table
uid VARCHAR(36) UNIQUE NOT NULL      -- Auto-generated UUID
is_trained BOOLEAN DEFAULT FALSE      -- Training status
trained_at DATETIME                   -- When trained
```

### UID Generation

- Uses Python's `uuid.uuid4()`
- Format: 36-character UUID
- Example: `a7824414-f025-63d3-9c4e-1234567890ab`
- Guaranteed unique
- Stored in database with index for fast lookup

### Training Status Tracking

```python
# Student object attributes
student.is_trained   # Boolean: True/False
student.trained_at   # DateTime: When trained
```

### Attendance Marking Logic

```python
# Only trained students can mark attendance
if student.is_trained:
    # Mark attendance
else:
    # Skip - student not trained
```

## 📝 Quick Reference

### URLs

| Page | URL | Access |
|------|-----|--------|
| Student Management | `/admin/students` | Admin Only |
| Register Student | `/register` | Admin Only |
| Capture Faces | `/capture/<roll>` | Admin Only |
| Train Model | `/train` | Admin Only |
| Mark Attendance | `/attendance` | All Users |
| User Management | `/admin/users` | Admin Only |

### Status Indicators

| Badge | Meaning |
|-------|---------|
| 🟢 **Trained** | Student can mark attendance |
| 🟡 **Pending** | Needs face capture/training |

### Workflow Summary

```
┌─────────────────┐
│  Admin Registers│
│  (UID Generated)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Capture Faces  │
│  (5-10 images)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Train Model   │
│ (Encode Faces)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Student Marks  │
│   Attendance    │
└─────────────────┘
```

## 🐛 Troubleshooting

### Student Cannot Mark Attendance

**Problem:** Student's face not recognized

**Solutions:**
1. Check if student is **trained** (green badge)
2. Retrain the model
3. Capture more face images
4. Ensure good lighting during attendance

### UID Not Showing

**Problem:** UID not generated

**Solution:**
- Re-register the student
- Check database migration completed
- Verify `uuid` module is available

### Training Fails

**Problem:** Model training fails

**Solutions:**
1. Ensure face images exist in dataset folder
2. Check images are valid (not corrupted)
3. Capture new images
4. Check server logs for errors

## 🎯 Best Practices

### For Admins

1. ✅ Verify student information before registration
2. ✅ Capture multiple face angles (5-10 images)
3. ✅ Train immediately after capturing
4. ✅ Keep backup of trained encodings
5. ✅ Regular monitoring of training status

### For Attendance

1. ✅ Ensure good lighting
2. ✅ Face camera directly
3. ✅ Remove glasses/masks if possible
4. ✅ Keep neutral expression
5. ✅ Wait for confirmation message

## 📚 API Endpoints

### Admin Only

```
POST   /register                    - Register new student (generates UID)
GET    /capture/<roll>              - Capture face images
POST   /api/upload_face             - Upload face image
GET    /train                       - Train face recognition model
GET    /admin/students              - View all students
```

### All Authenticated Users

```
POST   /api/recognize_attendance    - Mark attendance (trained only)
GET    /attendance                  - Attendance page
```

---

**Version:** 2.1.0  
**Last Updated:** March 2025  
**Author:** Face Attendance System Team
