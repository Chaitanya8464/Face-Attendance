# Deployment Notes

## Render Deployment

### Configuration
- **Runtime**: Docker
- **Build Command**: (auto-detected from Dockerfile)
- **Start Command**: (auto-detected from Dockerfile)

### Environment Variables
```
FLASK_ENV=production
PYTHONUNBUFFERED=1
SECRET_KEY=<generate-random-secret-key>
```

### Build Time
- First build: 10-15 minutes (dlib compilation)
- Subsequent builds: 2-5 minutes

### Important Notes
1. Free tier spins down after 15 minutes of inactivity
2. First request after spin-down takes ~30 seconds
3. SQLite database is ephemeral - consider PostgreSQL for production

## Railway Deployment

### Configuration
- Connect GitHub repository
- Auto-deploys on push to main branch
- Uses Dockerfile for build

### Environment Variables
```
PORT=8000
FLASK_ENV=production
SECRET_KEY=<generate-random-secret-key>
```

## Heroku Deployment

### Configuration
- Uses Procfile for web process
- Requires Heroku CLI

### Commands
```bash
heroku create attendance-face-recog
heroku config set FLASK_ENV=production
heroku config set SECRET_KEY=<generate-random-secret-key>
git push heroku main
heroku open
```

## Docker Local Testing

```bash
# Build image
docker build -t attendance-face-recog .

# Run container
docker run -p 8000:8000 attendance-face-recog

# Access application
open http://localhost:8000
```

## Troubleshooting

### Build fails on Render
- Check build logs in dashboard
- Ensure all dependencies in requirements.txt
- dlib compilation may fail - check CMake installation

### Database issues
- SQLite is file-based and may not persist on all platforms
- For production, migrate to PostgreSQL
- Add DATABASE_URL environment variable

### Camera not working in production
- Browsers require HTTPS for camera access
- Add SSL certificate or use reverse proxy
- Check browser console for permission errors

## Post-Deployment Checklist

- [ ] Test student registration
- [ ] Capture face images
- [ ] Train the model
- [ ] Test attendance recognition
- [ ] Verify dashboard displays correctly
- [ ] Test dark mode toggle
- [ ] Export CSV functionality
- [ ] Check error handling

## Performance Tips

1. **Enable caching** - Use Redis for session storage
2. **Optimize images** - Resize uploaded images
3. **Use CDN** - Serve static assets from CDN
4. **Database indexing** - Add indexes on frequently queried columns
5. **Background processing** - Use Celery for face encoding

## Security Considerations

1. Change SECRET_KEY in production
2. Enable HTTPS
3. Add rate limiting to API endpoints
4. Sanitize user inputs
5. Use environment variables for sensitive data
6. Regular dependency updates
