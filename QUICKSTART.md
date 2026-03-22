# Quick Start Guide

## Project Structure

This project is now organized with a clear separation between frontend and backend:

```
attendance-face-recog/
├── backend/          # Flask backend application
├── frontend/         # HTML templates and static assets
└── README.md         # Main documentation
```

## Running the Application

### Option 1: Direct Python (Development)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Run the application:**
   ```bash
   python app/app.py
   ```

4. **Access the application:**
   Open http://localhost:8000 in your browser

### Option 2: Using Flask CLI

```bash
cd backend
set FLASK_APP=app/app.py        # Windows
export FLASK_APP=app/app.py     # Linux/Mac
flask run --port 8000
```

### Option 3: Using Gunicorn (Production-like)

```bash
cd backend
gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 app.app:app
```

### Option 4: Using Docker

From the project root:
```bash
docker build -f backend/Dockerfile -t face-attendance .
docker run -p 8000:8000 face-attendance
```

## Default Login Credentials

- **Admin:** admin@faceattendance.com / admin123
  - ⚠️ **Change this immediately in production!**

## Troubleshooting

### Module Import Errors
Make sure you're running from the `backend` directory and your virtual environment is activated.

### Template Not Found Errors
The frontend directory must be at the same level as the backend directory.

### Database Errors
The database file (`database.db`) will be created automatically in the backend directory on first run.

## Next Steps

- [Backend Documentation](backend/README.md) - API endpoints, configuration
- [Frontend Documentation](frontend/README.md) - Templates, customization
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
