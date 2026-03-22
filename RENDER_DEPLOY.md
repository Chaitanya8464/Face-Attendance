# 🚀 Render Deployment Guide

## ✅ Fixed Issues

The Dockerfile path issue has been resolved:
- ✅ Created root-level `Dockerfile` for Render
- ✅ Updated `render.yaml` to use `./Dockerfile`
- ✅ Added root `.dockerignore` for optimized builds

---

## 📋 Deployment Steps

### 1. Push Changes to GitHub

```bash
# Add all the new files
git add .
git commit -m "Fix Render deployment - add root Dockerfile"
git push origin main
```

### 2. Deploy on Render

#### Option A: Fresh Deployment

1. Go to https://render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account
4. Select **"Face-Attendance"** repository
5. Render will detect `render.yaml` automatically
6. Click **"Apply"**

#### Option B: Fix Existing Deployment

If you already have a deployment:

1. Go to your Render Dashboard
2. Click on your service
3. Go to **"Settings"** tab
4. Scroll to **"Build & Deploy"**
5. Click **"Manual Deploy"**
6. Select branch: **main**
7. Click **"Deploy"**

---

## 🔧 Configuration

### Environment Variables (Auto-Set by render.yaml)

These are automatically configured:
- `FLASK_ENV=production`
- `PYTHONUNBUFFERED=1`
- `SECRET_KEY` (auto-generated)
- `DATABASE_URL` (from PostgreSQL)

### Optional: Add Email Configuration

In Render Dashboard → Environment:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## ⏱️ Build Timeline

**Total Build Time: 15-20 minutes**

1. **0-2 min:** Repository cloning
2. **2-5 min:** System dependencies (cmake, build-essential)
3. **5-15 min:** Python packages (dlib compilation - slowest part)
4. **15-18 min:** Final image build
5. **18-20 min:** Deployment and health check

**Monitor:** Go to Render Dashboard → Deployments tab → View logs

---

## 🎯 Post-Deployment

### 1. Create Admin User

After deployment succeeds:

1. Go to Render Dashboard
2. Click on your service
3. Go to **"Shell"** tab
4. Click **"Connect"**
5. Run:

```bash
cd /app
python3 << EOF
from backend.app.app import app, db
from backend.models import User

with app.app_context():
    # Create admin
    admin = User(
        email='admin@yoursite.com',
        username='admin',
        role='admin',
        is_verified=True
    )
    admin.set_password('ChangeMe123!')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin user created!')
    print('Email: admin@yoursite.com')
    print('Password: ChangeMe123!')
EOF
```

### 2. Test Your Deployment

Visit your Render URL: `https://your-app-name.onrender.com`

Test these endpoints:
- ✅ `/health` - Should return `{"status": "healthy"}`
- ✅ `/login` - Should load login page
- ✅ `/attendance` - Should load with camera (HTTPS enabled)

### 3. Change Admin Password Immediately!

Login with the admin credentials you created, then change the password.

---

## 🔍 Troubleshooting

### Build Fails with "No such file or directory"

**Error:** `failed to read dockerfile: open Dockerfile: no such file or directory`

**Solution:**
- ✅ Already fixed! Root `Dockerfile` created
- Push latest changes to GitHub
- Redeploy on Render

### Build Fails with Memory Error

**Error:** `error: failed to solve: process did not complete successfully`

**Cause:** dlib compilation ran out of memory

**Solution:**
1. Wait 5-10 minutes
2. Click **"Manual Deploy"** again
3. Render uses cached layers, second build usually succeeds

### Database Not Found

**Error:** `no such table: users`

**Solution:**
```bash
# In Render Shell
cd /app/backend
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"
```

### Camera Not Working

**Check:**
1. ✅ Using HTTPS URL (Render provides this automatically)
2. ✅ Browser permissions granted
3. ✅ Check browser console (F12) for errors

### Build Takes Too Long

**Normal:** First build takes 15-20 minutes (dlib compilation)
**Subsequent builds:** 2-5 minutes (uses cache)

---

## 📊 Render Dashboard Navigation

| Tab | Purpose |
|-----|---------|
| **Info** | Service URL, region, status |
| **Deployments** | Build history and logs |
| **Shell** | Command-line access to running container |
| **Logs** | Real-time application logs |
| **Metrics** | CPU, memory, request metrics |
| **Settings** | Environment variables, auto-deploy settings |

---

## 💰 Free Tier Limits

- ✅ **750 hours/month** (continuous uptime = ~30 days)
- ✅ **512 MB RAM**
- ✅ **Free PostgreSQL** (1 GB storage)
- ⚠️ **Sleeps after 15 min** of inactivity
  - Wakes up automatically on next request
  - First request after sleep takes ~30 seconds

---

## 🔗 Important URLs

After deployment, you'll get:

- **App URL:** `https://face-attendance-xxxx.onrender.com`
- **Admin Panel:** `https://face-attendance-xxxx.onrender.com/admin`
- **Health Check:** `https://face-attendance-xxxx.onrender.com/health`

---

## 📝 Quick Reference

### View Logs
```
Render Dashboard → Your Service → Logs
```

### Manual Deploy
```
Render Dashboard → Your Service → Settings → Manual Deploy
```

### Open Shell
```
Render Dashboard → Your Service → Shell → Connect
```

### Environment Variables
```
Render Dashboard → Your Service → Environment
```

---

## ✅ Deployment Checklist

Before deploying:
- [ ] All changes pushed to GitHub
- [ ] `Dockerfile` exists in root directory
- [ ] `render.yaml` exists in root directory
- [ ] `.dockerignore` exists in root directory

After deploying:
- [ ] Build completed successfully
- [ ] Health check passed
- [ ] Admin user created
- [ ] Can access login page
- [ ] Camera works on attendance page

---

## 🆘 Need Help?

### Render Support
- Docs: https://render.com/docs
- Status: https://status.render.com
- Support: https://render.com/support

### Common Commands (in Shell)
```bash
# Check if app is running
ps aux | grep gunicorn

# View recent logs
tail -f /app/logs/*.log

# Check disk space
df -h

# Check Python version
python3 --version

# List installed packages
pip list
```

---

## 🎉 Success Indicators

Your deployment is successful when:

1. ✅ Build status shows **"Live"** (green)
2. ✅ Health check passes
3. ✅ Can access homepage
4. ✅ Can login with admin account
5. ✅ Camera works on attendance page
6. ✅ No errors in logs

**Deployment complete! 🚀**
