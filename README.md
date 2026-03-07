# Attendance Face Recognition System

A Flask-based web application for automated attendance tracking using face recognition.

## Features

- **Student Registration**: Register students with name and roll number
- **Face Capture**: Capture and store face images for each student
- **Face Recognition**: Recognize faces and mark attendance automatically
- **Dashboard**: View attendance records and student information
- **Real-time Processing**: Mark attendance via webcam or image upload

## Local Development

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd attendance-face-recog
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open browser and go to: `http://localhost:8000`

### First Time Setup

1. Go to **Register** page and add student details
2. Capture face images for the student
3. Go to **Train** page to encode faces
4. Use **Attendance** page to mark attendance via face recognition
5. View records on **Dashboard** page

## Deploy to Render (Free Tier)

### Option 1: Using Render Dashboard

1. **Push code to GitHub/GitLab**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com) and sign in
   - Click **New +** → **Web Service**
   - Connect your GitHub/GitLab repository

3. **Configure the service**
   - **Name**: attendance-face-recog
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: main
   - **Root Directory**: (leave blank)
   - **Runtime**: Docker
   - **Docker Command**: (leave blank)

4. **Environment Variables**
   Add these in Render dashboard:
   ```
   FLASK_ENV=production
   PYTHONUNBUFFERED=1
   ```

5. **Deploy**
   - Click **Create Web Service**
   - Wait for build and deployment (first build takes ~10-15 minutes)

### Option 2: Using render.yaml

The `render.yaml` file is already configured. When you connect your repo, Render will auto-detect it.

### Important Notes for Render

- **Free tier limitations**: 
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down takes ~30 seconds to wake up
  - Limited to 750 hours/month (enough for continuous running)

- **Database**: SQLite is used. For production, consider migrating to PostgreSQL.

- **File Storage**: The `dataset` folder is excluded from git. After deployment:
  1. Register students via the web interface
  2. Capture face images through the browser
  3. Train the model using the Train page

## Project Structure

```
attendance-face-recog/
├── app.py              # Main Flask application
├── models.py           # Database models
├── face_utils.py       # Face recognition utilities
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration for Render
├── render.yaml         # Render deployment config
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── dataset/            # Stored face images (gitignored)
└── database.db         # SQLite database (gitignored)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/register` | GET/POST | Student registration |
| `/capture/<roll>` | GET | Face capture page |
| `/api/upload_face` | POST | Upload face image (JSON) |
| `/train` | GET | Train face recognition model |
| `/attendance` | GET | Attendance capture page |
| `/api/start_recognize` | POST | Recognize faces (server cam) |
| `/api/recognize_attendance` | POST | Recognize from uploaded image |
| `/dashboard` | GET | View attendance records |

## Troubleshooting

### Build fails on Render
- Check build logs in Render dashboard
- Ensure all dependencies are in requirements.txt
- First build takes longer due to dlib compilation

### Face recognition not working
- Ensure you've trained the model after adding students
- Check that face images are clear and well-lit
- Verify encodings.pkl is generated after training

### Database errors
- Delete database.db and restart to reset
- Ensure write permissions in production

## License

MIT License
