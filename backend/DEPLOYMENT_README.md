# Face Attendance System - Backend Deployment

This directory contains the backend ready for deployment on Render.

## Quick Deploy to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub/GitLab
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml` and set up:
   - Web service
   - PostgreSQL database
   - Environment variables

### Option 2: Manual Setup

1. **Create a new Web Service** on Render
2. **Connect your repository**
3. **Configure:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Starter (or higher for better performance)

4. **Add Environment Variables:**
   ```
   SECRET_KEY=<generate-a-secure-key>
   DATABASE_URL=<from-render-postgresql>
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=<your-email>
   MAIL_PASSWORD=<your-app-password>
   MAIL_DEFAULT_SENDER=noreply@faceattendance.com
   ```

5. **Create PostgreSQL Database:**
   - Go to "New +" → "PostgreSQL"
   - Create database
   - Copy the connection string
   - Add as `DATABASE_URL` environment variable

## Project Structure

```
backend/
├── app.py                 # Main Flask application (entry point)
├── models.py              # Database models
├── face_utils.py          # Face recognition utilities
├── auth_utils.py          # Authentication utilities
├── email_utils.py         # Email sending utilities
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── Dockerfile            # Docker configuration
├── Procfile              # Process file for Render
├── .dockerignore         # Docker ignore rules
└── .gitignore            # Git ignore rules
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Or with gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes (for production) |
| `MAIL_SERVER` | SMTP server | No (default: smtp.gmail.com) |
| `MAIL_PORT` | SMTP port | No (default: 587) |
| `MAIL_USE_TLS` | Use TLS for email | No (default: true) |
| `MAIL_USERNAME` | Email username | For email features |
| `MAIL_PASSWORD` | Email password | For email features |
| `MAIL_DEFAULT_SENDER` | Default sender email | No |

## Database Setup

The app uses:
- **SQLite** for local development (auto-created as `database.db`)
- **PostgreSQL** for production (Render PostgreSQL)

Database tables are auto-created on first run. A default admin user is created:
- **Email:** admin@faceattendance.com
- **Password:** admin123

**⚠️ Change the default password immediately!**

## Face Recognition Setup

The system stores:
- **Face encodings:** In `dataset/` directory
- **Student photos:** In `dataset/<roll_number>/` subdirectories

On Render, these files persist across deployments if you add persistent disk storage.

## Troubleshooting

### Build Fails
- Check `requirements.txt` is in the backend root
- Ensure Python version is 3.11
- Increase build timeout if dlib compilation times out

### Database Errors
- Verify `DATABASE_URL` is correct
- Check PostgreSQL database is created
- Ensure connection string uses `postgresql://` (not `postgres://`)

### Face Recognition Fails
- Ensure `dataset/` directory exists
- Check file permissions
- Verify dlib and face_recognition are installed

## Support

For issues, check:
- [Render Documentation](https://render.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com)
- Application logs in Render dashboard
