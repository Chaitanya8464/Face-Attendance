# Vercel Deployment Guide

## Important Notes

⚠️ **Vercel is designed for static sites and serverless functions, NOT for traditional Flask apps with persistent databases.**

### Limitations on Vercel:
1. **No persistent database** - SQLite won't work (files are read-only)
2. **No file writes** - Can't save face encodings or dataset files
3. **Serverless timeout** - Max 10 seconds execution time
4. **No background processes** - Face recognition may timeout

## Recommended Alternatives

For this Flask face recognition app, use:
- **Render** (recommended) - Free tier with persistent storage
- **Railway** - Easy deployment with database support
- **Heroku** - Traditional PaaS with add-ons
- **AWS/GCP/Azure** - Full control but more complex

## If You Still Want to Deploy on Vercel

### Prerequisites:
1. Use PostgreSQL database (not SQLite)
2. Store face encodings in database, not files
3. Set up external storage for images (S3, Cloudinary, etc.)

### Steps:

1. **Update Database Configuration:**
   ```python
   # Use environment variable for database URL
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   ```

2. **Configure Vercel:**
   - Add `vercel.json` (already created)
   - Add `requirements.txt` at root (already created)
   - Set up `api/index.py` (already created)

3. **Deploy:**
   ```bash
   vercel login
   vercel --prod
   ```

4. **Set Environment Variables in Vercel Dashboard:**
   - `DATABASE_URL` - PostgreSQL connection string
   - `SECRET_KEY` - Random secure string
   - `MAIL_USERNAME` - Email for notifications
   - `MAIL_PASSWORD` - Email password

## Better Alternative: Deploy to Render

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: face-attendance
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "gunicorn backend.app.app:app"
       envVars:
         - key: FLASK_ENV
           value: production
   ```

2. **Deploy:**
   - Push to GitHub
   - Connect repository to Render
   - Deploy automatically

## Fixing CSS Issues on Vercel

If CSS is not loading:

1. **Check static file route** - Already added `/static/<path:filename>` route
2. **Verify file paths** - Ensure static files are in `frontend/templates/static/`
3. **Check vercel.json** - All requests should route through Flask
4. **Clear Vercel cache** - Redeploy with `vercel --prod --force`

### Debug Steps:

1. Open browser DevTools (F12)
2. Check Network tab for failed static file requests
3. Check Vercel function logs for errors
4. Verify `url_for('static', ...)` generates correct URLs
