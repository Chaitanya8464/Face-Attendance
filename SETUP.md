# SETUP GUIDE

Quick setup instructions for developers.

## Local Development (Windows)

### 1. Prerequisites
- Python 3.11 or higher
- Git
- CMake (for dlib compilation)

### 2. Clone and Setup
```bash
git clone <repository-url>
cd attendance-face-recog
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install CMake first if not already installed
pip install cmake
pip install -r requirements.txt
```

**NOTE:** If `dlib` installation fails:
- Install Visual Studio Build Tools with C++ workload
- Or use pre-built wheels: `pip install dlib --only-binary :all:`

### 4. Run the Application
```bash
python app.py
```

Visit: http://localhost:8000

## First Time Usage

1. **Register a Student**
   - Go to /register
   - Enter name and roll number
   - Click "Proceed to Capture"

2. **Capture Face Images**
   - Allow camera access
   - Capture 5-10 images from different angles
   - Click "Save & Train"

3. **Train the Model**
   - Go to /train
   - Click "Train Model"
   - Wait for encoding to complete

4. **Mark Attendance**
   - Go to /attendance
   - Click "Start Recognition"
   - Show face to camera

## Deployment

### Render
1. Push code to GitHub
2. Connect repository to Render
3. Use Docker runtime
4. Deploy

### Railway
1. Connect GitHub repository
2. Deploy automatically
3. Add PORT environment variable if needed

## Troubleshooting

### Camera not working
- Check browser permissions
- Ensure HTTPS in production (browsers block camera on HTTP)
- Try different browser

### Face not recognized
- Ensure good lighting
- Capture more training images
- Retrain the model

### Build fails on deployment
- Check build logs
- Ensure all dependencies in requirements.txt
- First build takes 10-15 minutes (dlib compilation)

## Database Reset

To reset everything:
```bash
# Delete these files
del database.db
del encodings.pkl
del dataset\*.jpg
```

## Testing

```bash
# Run tests
python -m pytest tests/

# Or with unittest
python -m unittest discover tests
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Module not found | Activate venv, reinstall requirements |
| Camera error | Check permissions, use HTTPS |
| Slow recognition | Reduce frame size in face_utils.py |
| Database locked | Close other connections, restart |

## Development Tips

- Use `flask run` instead of `python app.py` for auto-reload
- Set `FLASK_ENV=development` for debug mode
- Check browser console for JavaScript errors
- Use browser dev tools to debug camera issues

## Project Structure

```
attendance-face-recog/
├── app.py              # Main application
├── models.py           # Database models
├── face_utils.py       # Face recognition logic
├── requirements.txt    # Dependencies
├── tests/              # Test files
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── dataset/            # Face images (gitignored)
└── database.db         # SQLite database (gitignored)
```

## Need Help?

Check these files:
- README.md - Full documentation
- CHANGELOG.md - Version history
- .env.example - Environment variables
