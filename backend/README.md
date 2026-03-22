# Backend - Face Recognition Attendance System

This directory contains the Flask backend application for the face recognition attendance system.

## Directory Structure

```
backend/
├── app/                  # Main Flask application
│   └── app.py           # Main application entry point
├── models/              # Database models (moved to backend root)
├── utils/               # Utility modules (moved to backend root)
├── config/              # Configuration files
├── migrations/          # Database migration scripts
├── tests/               # Test files
├── dataset/             # Face dataset storage (git-ignored)
├── .env.example         # Environment variables template
├── Dockerfile           # Docker configuration
├── Procfile             # Heroku/Render deployment config
└── requirements.txt     # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- CMake (for dlib compilation)
- C++ compiler (for dlib compilation)

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and update the following:
   - `SECRET_KEY`: Generate a secure random key
   - `MAIL_USERNAME`: Your SMTP email
   - `MAIL_PASSWORD`: Your SMTP password

5. **Run the application:**
   ```bash
   python app/app.py
   ```
   Or with gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:8000 --workers 1 app.app:app
   ```

## Default Credentials

- **Admin:** admin@faceattendance.com / admin123
  - ⚠️ **Change this immediately in production!**

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /signup` - User registration
- `GET /logout` - User logout
- `GET/POST /forgot-password` - Password reset request
- `GET/POST /reset-password/<token>` - Password reset

### Student
- `GET/POST /student-login` - Student login
- `GET /student-dashboard` - Student dashboard
- `GET /student-logout` - Student logout
- `GET /student/attendance` - View attendance history
- `GET/POST /student/change-password` - Change password
- `GET/POST /student/forgot-password` - Password reset
- `GET/POST /student/profile` - View/edit profile

### Admin/Teacher
- `GET /dashboard` - Role-based dashboard
- `GET /capture` - Capture faces for attendance
- `GET /train` - Train face recognition model
- `GET /attendance` - View all attendance records

## Database

The application uses SQLite by default. The database file (`database.db`) is stored in the backend directory.

To migrate to PostgreSQL for production:
1. Update `DATABASE_URL` in `.env`
2. Run migration scripts from `migrations/` folder

## Deployment

### Docker
```bash
docker build -t face-attendance .
docker run -p 8000:8000 face-attendance
```

### Render/Railway
The application is configured for deployment via the `Dockerfile` and `Procfile`.

## Troubleshooting

### dlib installation fails
- Ensure CMake is installed: `cmake --version`
- Install Visual C++ Build Tools (Windows)
- Try: `pip install dlib --no-cache-dir`

### Face recognition not working
- Ensure `dataset/` directory exists and has proper permissions
- Check camera access permissions
- Verify face_recognition library is installed correctly

## Project Structure Notes

- **Templates and Static files** are located in the `../frontend` directory
- The Flask app is configured to serve files from the frontend directory
- All business logic remains in the backend
