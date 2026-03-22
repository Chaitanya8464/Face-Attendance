# Face Recognition Attendance System

A complete attendance management system using face recognition technology. This project is structured with a clear separation between frontend and backend.

## Project Structure

```
attendance-face-recog/
├── backend/              # Flask backend application
│   ├── app/             # Main Flask application
│   ├── migrations/      # Database migration scripts
│   ├── tests/           # Test files
│   ├── dataset/         # Face dataset (git-ignored)
│   ├── .env.example     # Environment variables template
│   ├── Dockerfile       # Docker configuration
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Backend documentation
│
├── frontend/            # Frontend templates and static assets
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # CSS and JavaScript files
│   └── README.md        # Frontend documentation
│
├── .gitignore           # Git ignore rules
├── render.yaml          # Render deployment config
└── README.md            # This file
```

## Features

- **Face Recognition Attendance**: Mark attendance using facial recognition
- **Role-Based Access**: Admin, Teacher, and Student roles
- **Real-Time Capture**: Live camera feed for face detection
- **Attendance Reports**: View and export attendance records
- **Email Verification**: User email verification and password reset
- **Responsive Design**: Works on desktop and mobile devices
- **Docker Support**: Easy deployment with Docker

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- CMake (for dlib)
- C++ compiler

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd attendance-face-recog
   ```

2. **Set up backend:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   copy .env.example .env
   ```

3. **Run the application:**
   ```bash
   python app/app.py
   ```

4. **Access the application:**
   Open http://localhost:8000 in your browser

### Default Credentials

- **Admin:** admin@faceattendance.com / admin123
  - ⚠️ Change this immediately!

## Documentation

- [Backend Documentation](backend/README.md) - Setup, API endpoints, deployment
- [Frontend Documentation](frontend/README.md) - Templates, static assets, customization

## Deployment

### Docker

```bash
# From project root
docker build -f backend/Dockerfile -t face-attendance .
docker run -p 8000:8000 face-attendance
```

### Render/Railway

Connect your repository to Render or Railway. The `render.yaml` and `backend/Procfile` handle automatic deployment.

## Development

### Running in Development Mode

```bash
cd backend
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac
python app/app.py
```

### Database Migrations

Migration scripts are located in `backend/migrations/`. Run them in order:

```bash
cd backend
python migrations/migrate_db.py
python migrations/migrate_db_v2.py
# ... and so on
```

## Technologies Used

### Backend
- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **Flask-Mail** - Email support
- **face_recognition** - Face detection and recognition
- **OpenCV** - Image processing
- **dlib** - Machine learning library

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript** - Client-side interactions
- **Jinja2** - Template engine
- **WebRTC** - Camera access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Check the documentation in `backend/README.md` and `frontend/README.md`
- Open an issue on GitHub

## Acknowledgments

- Face recognition powered by [face_recognition](https://github.com/ageitgey/face_recognition)
- Built with [Flask](https://flask.palletsprojects.com/)
