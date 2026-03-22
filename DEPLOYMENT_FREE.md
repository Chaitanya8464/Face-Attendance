# 🚀 Free Deployment Guide

## Overview

This guide covers **3 best free deployment options** for your Face Recognition Attendance System:

1. **Render** - Best overall (free PostgreSQL, easy setup)
2. **Railway** - Great alternative (generous free tier)
3. **Hugging Face Spaces** - Simplest for demos (CPU only)

---

## ⚠️ Important Notes Before Deploying

### Camera Requirements
- **HTTPS is mandatory** for camera access in production
- All platforms below provide free HTTPS automatically

### Face Recognition Limitations
- **dlib compilation takes 10-15 minutes** on free tiers
- **Build can fail** on platforms with low memory (512MB)
- **Solution**: Use pre-built wheels or platforms with more RAM

### Database
- **SQLite** works but has concurrency limitations
- **PostgreSQL** recommended for production (free on Render)

---

## Option 1: Render (RECOMMENDED) ⭐

**Best for:** Production-ready deployment with PostgreSQL

### Free Tier Limits
- ✅ **750 hours/month** (continuous uptime)
- ✅ **512 MB RAM**
- ✅ **Free PostgreSQL database**
- ✅ **Automatic HTTPS**
- ⚠️ **Sleeps after 15 min** of inactivity (wakes on request)

### Step-by-Step Setup

#### 1. Prepare Your Repository

```bash
# Make sure your code is on GitHub
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/attendance-face-recog.git
git push -u origin main
```

#### 2. Create render.yaml File

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: attendance-face-recog
    env: docker
    region: oregon
    plan: free
    dockerfilePath: ./backend/Dockerfile
    healthCheckPath: /health
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: attendance-db
          property: connectionString

databases:
  - name: attendance-db
    plan: free
    region: oregon
```

#### 3. Update Dockerfile for PostgreSQL

Edit `backend/Dockerfile`:

```dockerfile
# Add psycopg2-binary for PostgreSQL
RUN pip install --no-cache-dir \
    face_recognition==1.3.0 \
    flask==2.3.2 \
    flask_sqlalchemy==3.0.3 \
    Werkzeug==2.3.7 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.9
```

#### 4. Deploy on Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Select your `render.yaml` file
6. Click **"Apply"**

#### 5. Wait for Build

- **Build time:** 15-20 minutes (dlib compilation)
- **Monitor:** Check Deployments tab for progress
- **First deploy:** May fail due to memory - retry once

#### 5. Configure Environment Variables

In Render Dashboard:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### 6. Run Database Migrations

After first deploy:
1. Go to **Shell** in Render dashboard
2. Run:
```bash
cd backend
python migrations/migrate_db.py
```

### ✅ Render Pros
- Free PostgreSQL database
- Automatic HTTPS
- Easy deployment
- Health checks built-in

### ❌ Render Cons
- Sleeps after 15 min inactivity
- 512MB RAM (build might fail)

---

## Option 2: Railway

**Best for:** More generous free tier, no sleep

### Free Tier Limits
- ✅ **500 hours/month**
- ✅ **1 GB RAM** (better for dlib)
- ✅ **$5 free credit/month**
- ✅ **No sleep**
- ⚠️ **No free PostgreSQL** (use SQLite or external)

### Step-by-Step Setup

#### 1. Prepare Repository

Same as Render (push to GitHub)

#### 2. Create railway.json

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 backend.app.app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 3. Update Procfile

Edit `backend/Procfile`:

```
web: gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app.app:app
```

#### 4. Deploy on Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway auto-detects Dockerfile

#### 5. Configure Variables

In Railway Dashboard → Variables:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=8000
```

#### 6. Add Domain (Optional)

- Railway provides free `*.railway.app` domain
- Or add custom domain in Settings

### ✅ Railway Pros
- More RAM (1GB)
- No sleep
- Faster builds
- Better for dlib compilation

### ❌ Railway Cons
- No free PostgreSQL (use SQLite or external DB)
- $5 credit expires monthly

---

## Option 3: Hugging Face Spaces

**Best for:** Quick demos, testing

### Free Tier Limits
- ✅ **Unlimited hours**
- ✅ **2 CPU cores**
- ✅ **16 GB RAM** (excellent!)
- ✅ **Free HTTPS**
- ⚠️ **Public by default**
- ⚠️ **No persistent storage**

### Step-by-Step Setup

#### 1. Create Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Name: `attendance-face-recog`
4. License: MIT
5. **Space SDK:** Select **"Docker"**
6. Click **"Create Space"**

#### 2. Create Dockerfile for HF

Create `Dockerfile` in root (different from backend):

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    cmake build-essential libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "backend.app.app:app"]
```

#### 3. Push to Hugging Face

```bash
# Install huggingface-cli
pip install huggingface_hub

# Login
huggingface-cli login

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/attendance-face-recog

# Copy files
cp -r backend/* attendance-face-recog/
cp Dockerfile attendance-face-recog/

# Push
cd attendance-face-recog
git add .
git commit -m "Deploy app"
git push
```

#### 4. Configure Settings

In Space Settings:
- Set **Hardware:** CPU Basic (free)
- Set **Visibility:** Public (free tier requirement)

### ✅ Hugging Face Pros
- Most RAM (16GB)
- Fastest dlib compilation
- No sleep
- Easy deployment

### ❌ Hugging Face Cons
- Public by default (anyone can see)
- No persistent storage (database resets)
- Not suitable for production data

---

## Option 4: Vercel + External DB

**Best for:** Frontend-heavy apps (NOT recommended for this project)

⚠️ **Not recommended** because:
- Face recognition requires heavy backend processing
- Vercel is optimized for frontend/serverless
- dlib compilation not supported
- 10 second timeout limit on serverless functions

---

## Database Options

### SQLite (Simplest)
```python
# In backend/app/app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
```
- ✅ No setup required
- ✅ Works on all platforms
- ❌ Concurrent access issues
- ❌ Data lost on some platforms (Hugging Face)

### PostgreSQL (Recommended)
```python
# Use environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

**Free PostgreSQL Options:**

1. **Render PostgreSQL** (included)
   - Free 1GB storage
   - Auto-created with render.yaml

2. **Neon.tech**
   - Free 500MB
   - Serverless PostgreSQL
   - https://neon.tech

3. **Supabase**
   - Free 500MB
   - Full PostgreSQL
   - https://supabase.com

4. **Aiven**
   - Free 5GB (limited time)
   - https://aiven.io

---

## Email Configuration (Optional)

For password reset and verification emails:

### Gmail (Free)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # NOT your regular password
```

**Get Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Go to App Passwords
4. Generate password for "Mail"
5. Use this password in `.env`

### Alternative: SendGrid (Free 100 emails/day)
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

---

## Pre-Deployment Checklist

### 1. Update Configuration

Edit `backend/app/app.py`:
```python
# Use environment variable for database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f"sqlite:///{os.path.join(PROJECT_ROOT, 'database.db')}"
)
```

### 2. Create .dockerignore

Create `backend/.dockerignore`:
```
__pycache__/
*.pyc
*.pyo
.env
venv/
.git/
*.db
dataset/
instance/
```

### 3. Test Locally with Production Settings

```bash
cd backend
export FLASK_ENV=production
export SECRET_KEY=test-key-123
python app/app.py
```

### 4. Update Security Settings

In `backend/app/app.py`:
```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

### 5. Add Health Check

Already exists at `/health` endpoint:
```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

---

## Post-Deployment Steps

### 1. Create Admin User

After deployment, create admin via shell:

**Render:**
1. Go to Dashboard → Shell
2. Run:
```bash
cd backend
python
```

```python
from app import app, db, User
with app.app_context():
    admin = User(email='admin@yoursite.com', username='admin', role='admin', is_verified=True)
    admin.set_password('change-me-immediately')
    db.session.add(admin)
    db.session.commit()
    print('Admin created!')
```

### 2. Update Environment Variables

Set these in your platform's dashboard:
```env
FLASK_ENV=production
SECRET_KEY=<generate-random-32-char-string>
DATABASE_URL=<from your platform>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Test Camera Access

1. Visit your deployed URL
2. Go to `/attendance`
3. Allow camera permission
4. Test face recognition

### 4. Migrate Database

If using PostgreSQL:
```bash
# In platform shell
cd backend
python migrations/migrate_db.py
```

---

## Troubleshooting

### Build Fails (Memory Error)

**Render:**
- Wait 5 minutes and retry
- Build cache helps subsequent builds

**Railway:**
- Has more RAM, should work better
- Check build logs for specific errors

**Solution:** Use pre-built Docker image:
```dockerfile
FROM python:3.11-slim

# Use pre-built dlib wheel
RUN pip install dlib==19.24.2 --index-url https://pypi.org/simple
RUN pip install face_recognition==1.3.0
```

### Camera Not Working

1. **Check HTTPS:** Must use HTTPS (all platforms provide this)
2. **Browser Permissions:** Allow camera access
3. **Browser Console:** Check for errors (F12)

### Database Errors

**SQLite not persisting:**
- Some platforms reset filesystem (Hugging Face)
- Use external PostgreSQL instead

**PostgreSQL connection failed:**
- Check DATABASE_URL format
- Verify credentials in dashboard

### dlib Compilation Fails

```dockerfile
# Use specific versions that compile better
RUN pip install numpy==1.26.2
RUN pip install dlib==19.24.2 --no-cache-dir
RUN pip install face_recognition==1.3.0
```

---

## Quick Start Commands

### For Render
```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy automatically triggers
# Monitor at: https://dashboard.render.com

# 3. Check logs
# Dashboard → Logs tab
```

### For Railway
```bash
# 1. Push to GitHub
git push origin main

# 2. Railway auto-deploys
# Monitor at: https://railway.app
```

### For Hugging Face
```bash
# 1. Clone space
git clone https://huggingface.co/spaces/YOUR_USERNAME/attendance-face-recog

# 2. Copy files
cp -r backend/* attendance-face-recog/
cp Dockerfile attendance-face-recog/

# 3. Push
cd attendance-face-recog
git add .
git commit -m "Update"
git push
```

---

## Comparison Table

| Feature | Render | Railway | Hugging Face |
|---------|--------|---------|--------------|
| **Free Hours** | 750/month | 500 hours | Unlimited |
| **RAM** | 512 MB | 1 GB | 16 GB |
| **Database** | ✅ Free PostgreSQL | ❌ External only | ❌ Not persistent |
| **Sleep** | ⚠️ 15 min inactivity | ✅ No sleep | ✅ No sleep |
| **HTTPS** | ✅ Free | ✅ Free | ✅ Free |
| **Build Time** | 15-20 min | 10-15 min | 5-10 min |
| **Best For** | Production | Testing | Demos |

---

## Recommended Setup

**For Production:**
- **Platform:** Render
- **Database:** Render PostgreSQL (free)
- **Email:** Gmail SMTP (free)
- **Total Cost:** $0/month

**For Testing:**
- **Platform:** Railway
- **Database:** SQLite
- **Total Cost:** $0/month

**For Demo:**
- **Platform:** Hugging Face Spaces
- **Database:** SQLite (resets on redeploy)
- **Total Cost:** $0/month

---

## Links

- **Render:** https://render.com
- **Railway:** https://railway.app
- **Hugging Face:** https://huggingface.co/spaces
- **Neon PostgreSQL:** https://neon.tech
- **Supabase:** https://supabase.com

---

## Need Help?

1. Check platform documentation
2. Review build logs for errors
3. Test locally with production settings first
4. Start with Railway (easiest for dlib)
5. Move to Render for production

**Good luck with your deployment! 🚀**
