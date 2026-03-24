# CSS Not Loading on Vercel - Fix Summary

## Problem
When deploying to Vercel, CSS and static files are not loading because:
1. Vercel uses serverless architecture
2. Static file serving needs explicit configuration
3. Flask's default static file handling doesn't work out-of-the-box on Vercel

## Files Created/Modified

### 1. `vercel.json` (Created at root)
Configures Vercel to route all requests through Flask:
```json
{
  "version": 2,
  "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
  "routes": [
    {"src": "/static/(.*)", "dest": "api/index.py"},
    {"src": "/(.*)", "dest": "api/index.py"}
  ]
}
```

### 2. `api/index.py` (Created at root)
Vercel serverless function entry point that wraps the Flask app.

### 3. `backend/app/app.py` (Modified)
- Added explicit `static_url_path='/static'`
- Added custom `/static/<path:filename>` route to serve files
- Updated static_folder path to `templates/static`

### 4. `requirements.txt` (Copied to root)
Vercel needs requirements.txt at project root.

### 5. `render.yaml` (Created)
Alternative deployment config for Render.com (recommended over Vercel).

## Deployment Steps

### For Vercel:

1. **Push all changes to Git:**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel login
   vercel --prod
   ```

3. **Set Environment Variables in Vercel Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add `SECRET_KEY` with a random secure value
   - Redeploy

### For Render (Recommended):

1. **Push to GitHub**

2. **Deploy on Render:**
   - Go to render.com
   - Create New Web Service
   - Connect your GitHub repo
   - Use these settings:
     - Build Command: `pip install -r backend/requirements.txt`
     - Start Command: `gunicorn --chdir backend/app app:app`
   - Add environment variables
   - Deploy

## Verification

After deployment:

1. Open your deployed site
2. Press F12 → Network tab
3. Refresh the page
4. Check if `styles.css` loads with status 200
5. If still failing, check Vercel Function logs

## Important Notes

⚠️ **Vercel Limitations for this app:**
- SQLite database won't persist (use PostgreSQL)
- Can't write files (face encodings will be lost)
- 10-second timeout (face recognition may fail)
- No background processes

**Recommendation:** Use **Render** or **Railway** instead of Vercel for this face recognition app, as they support:
- Persistent databases
- File storage
- Longer timeouts
- Background processes

## Troubleshooting

### CSS still not loading?

1. **Check browser console:**
   - F12 → Console → Look for 404 errors

2. **Check Vercel logs:**
   - Vercel Dashboard → Deployments → Click latest → Function Logs

3. **Force redeploy:**
   ```bash
   vercel --prod --force
   ```

4. **Verify static files exist:**
   - Check `frontend/templates/static/css/styles.css` exists
   - Check `frontend/templates/static/js/main.js` exists

### Database errors?

Vercel doesn't support SQLite. You need to:
1. Use PostgreSQL (addons.neon.tech or similar)
2. Update `SQLALCHEMY_DATABASE_URI` in code
3. Set `DATABASE_URL` environment variable in Vercel
