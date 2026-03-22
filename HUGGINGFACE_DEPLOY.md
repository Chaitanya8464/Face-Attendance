# 🚀 Hugging Face Spaces Deployment Guide

## Deploy in 5 Minutes!

### Step 1: Create a Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `face-attendance` (or your choice)
   - **License:** MIT
   - **Space SDK:** Select **Docker**
   - **Visibility:** Public (free tier requirement)
3. Click **"Create Space"**

---

### Step 2: Install Hugging Face CLI

```bash
pip install huggingface_hub
```

---

### Step 3: Login to Hugging Face

```bash
huggingface-cli login
```

You'll be asked for your Hugging Face token:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token (write permission)
3. Copy and paste the token

---

### Step 4: Clone Your Space

```bash
# Replace YOUR_USERNAME with your Hugging Face username
git clone https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
```

---

### Step 5: Copy Project Files

```bash
# Copy backend files
cp -r backend/* face-attendance/backend/

# Copy frontend files
cp -r frontend/ face-attendance/frontend/

# Copy Dockerfile
cp Dockerfile.huggingface face-attendance/Dockerfile

# Copy requirements
cp backend/requirements_minimal.txt face-attendance/
```

**On Windows (PowerShell):**
```powershell
Copy-Item -Path backend\* -Destination face-attendance\backend\ -Recurse
Copy-Item -Path frontend\ -Destination face-attendance\frontend\ -Recurse
Copy-Item -Path Dockerfile.huggingface -Destination face-attendance\Dockerfile
Copy-Item -Path backend\requirements_minimal.txt -Destination face-attendance\
```

---

### Step 6: Push to Hugging Face

```bash
cd face-attendance

# Add all files
git add .

# Commit
git commit -m "Deploy face attendance system"

# Push
git push
```

---

### Step 7: Wait for Build

- **Build time:** 5-10 minutes (pre-built image = fast!)
- **Monitor:** Go to your Space page → "App" tab
- **Status:** Building → Running

---

### Step 8: Access Your App

Your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
```

---

## ✅ After Deployment

### Create Admin User

1. Go to your Space → "Settings" tab
2. Scroll to **"Variables and secrets"**
3. Click **"New secret"**
4. Add:
   - Name: `CREATE_ADMIN`
   - Value: `true`

Or use the Space terminal:

1. Go to Settings → "Factory"
2. Click **"Open Terminal"**
3. Run:

```bash
cd /app
python3 << EOF
from backend.app.app import app, db
from backend.models import User

with app.app_context():
    admin = User(
        email='admin@site.com',
        username='admin',
        role='admin',
        is_verified=True
    )
    admin.set_password('ChangeMe123!')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin created!')
EOF
```

### Test Your App

Visit: `https://huggingface.co/spaces/YOUR_USERNAME/face-attendance`

- ✅ `/health` - Returns `{"status": "healthy"}`
- ✅ `/login` - Login page loads
- ✅ `/attendance` - Camera works (HTTPS enabled)

---

## 🔧 Configuration

### Environment Variables

In Space Settings → "Variables and secrets":

```
FLASK_ENV=production
SECRET_KEY=your-random-32-character-string
CREATE_ADMIN=true  # Optional: creates default admin
```

---

## ⚠️ Important Notes

### Public Only
- Free tier spaces are **public**
- Anyone can see your code and app
- **Don't deploy sensitive data**

### Storage Resets
- Files are **deleted on redeploy**
- Database resets each deployment
- For persistent storage, use external database

### Camera Access
- ✅ HTTPS is automatic
- ✅ Camera works in browsers
- ✅ No additional configuration needed

---

## 🆘 Troubleshooting

### Build Fails

**Check logs in:**
- Space page → "App" tab
- Click "See logs"

**Common fixes:**
```bash
# Make sure Dockerfile.huggingface exists
ls -la Dockerfile

# Check requirements file
cat requirements_minimal.txt

# Redeploy
git add .
git commit -m "Fix deployment"
git push
```

### App Won't Start

**Check logs:**
```bash
# In Space terminal (Settings → Factory → Open Terminal)
tail -f /app/logs/*.log
```

**Common issues:**
- Missing `SECRET_KEY` → Add in Settings
- Port wrong → Must be 7860
- Import errors → Check file paths

### Camera Not Working

- ✅ Ensure you're using HTTPS (automatic on HF)
- ✅ Allow camera permissions in browser
- ✅ Check browser console (F12) for errors

---

## 📊 Space Dashboard

| Tab | Purpose |
|-----|---------|
| **App** | Live app and build logs |
| **Files** | View/edit source code |
| **Settings** | Environment variables, hardware |
| **Community** | Discussions and comments |

---

## 💰 Free Tier Limits

- ✅ **Unlimited hours** (no sleep!)
- ✅ **16 GB RAM** (fastest builds!)
- ✅ **2 CPU cores**
- ✅ **Free HTTPS**
- ⚠️ **Public only** (code visible to everyone)
- ⚠️ **No persistent storage** (resets on redeploy)

---

## 🎯 Quick Commands

### Update Your Space
```bash
cd face-attendance
# Make changes
git add .
git commit -m "Update"
git push
```

### View Logs
```
Space → App tab → See logs
```

### Open Terminal
```
Space → Settings → Factory → Open Terminal
```

### Delete Space
```
Space → Settings → Scroll down → Delete this space
```

---

## 🔗 Useful Links

- **Hugging Face Spaces:** https://huggingface.co/spaces
- **Documentation:** https://huggingface.co/docs/hub/spaces
- **Docker SDK:** https://huggingface.co/docs/hub/spaces-sdks-docker
- **Your Spaces:** https://huggingface.co/spaces/YOUR_USERNAME

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Hugging Face account created
- [ ] Space created (Docker SDK)
- [ ] huggingface_hub installed
- [ ] Logged in with token

After deploying:
- [ ] Build completed successfully
- [ ] App shows "Running"
- [ ] Can access homepage
- [ ] Camera works on attendance page
- [ ] Admin user created

---

## 🎉 Success!

Your face attendance system is now live on Hugging Face Spaces!

**Share your app:**
```
https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
```

**Need more help?** Check the logs in the App tab or open a terminal in Settings.
