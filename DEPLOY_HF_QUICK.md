# ⚡ Quick Deploy to Hugging Face Spaces

## 3-Minute Deployment

### Option 1: Use Deployment Script (Easiest)

**Windows:**
```bash
deploy-huggingface.bat
```

Just run the script and follow the prompts!

---

### Option 2: Manual Deployment

#### 1. Create Space
Go to https://huggingface.co/new-space
- Name: `face-attendance`
- SDK: **Docker**
- Visibility: **Public**

#### 2. Install & Login
```bash
pip install huggingface_hub
huggingface-cli login
```

#### 3. Clone Your Space
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
cd face-attendance
```

#### 4. Copy Files

**Linux/Mac:**
```bash
cp -r ../backend/* backend/
cp -r ../frontend/ frontend/
cp ../Dockerfile.huggingface Dockerfile
cp ../backend/requirements_minimal.txt .
```

**Windows (PowerShell):**
```powershell
Copy-Item -Path ..\backend\* -Destination backend\ -Recurse -Force
Copy-Item -Path ..\frontend\ -Destination frontend\ -Recurse -Force
Copy-Item -Path ..\Dockerfile.huggingface -Destination .
Copy-Item -Path ..\backend\requirements_minimal.txt -Destination .
```

#### 5. Push
```bash
git add .
git commit -m "Deploy"
git push
```

---

## ✅ Done!

Your app will be live in **5-10 minutes** at:
```
https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
```

---

## 🎯 After Deployment

### Create Admin User

In Space Settings → Factory → Open Terminal:

```bash
cd /app
python3 << EOF
from backend.app.app import app, db
from backend.models import User

with app.app_context():
    admin = User(email='admin@site.com', username='admin', 
                 role='admin', is_verified=True)
    admin.set_password('ChangeMe123!')
    db.session.add(admin)
    db.session.commit()
    print('Admin created!')
EOF
```

### Test Your App

Visit: `https://huggingface.co/spaces/YOUR_USERNAME/face-attendance`

---

## 💡 Why Hugging Face Spaces?

| Feature | Hugging Face | Railway | Render |
|---------|--------------|---------|--------|
| **RAM** | 16 GB ✅ | 1 GB | 512 MB |
| **Build Time** | 5 min ✅ | 10 min | 15 min |
| **Timeout** | None ✅ | 10 min | 15 min |
| **Sleep** | No ✅ | No | Yes |
| **HTTPS** | Yes ✅ | Yes | Yes |
| **Cost** | Free ✅ | Free | Free |

---

## 🆘 Need Help?

- **Build logs:** Space → App tab → See logs
- **Terminal:** Space → Settings → Factory → Open Terminal
- **Docs:** `HUGGINGFACE_DEPLOY.md`

---

**Your app is live in minutes! 🚀**
