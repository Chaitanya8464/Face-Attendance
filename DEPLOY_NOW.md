# 🚀 Deploy to Hugging Face - RIGHT NOW!

## Step-by-Step (5 Minutes)

### Step 1: Create Hugging Face Account
1. Go to https://huggingface.co
2. Click **"Sign Up"**
3. Sign up with GitHub (easiest) or email

**Done?** Continue to Step 2.

---

### Step 2: Create a Space
1. Go to https://huggingface.co/new-space
2. Fill in:
   ```
   Space name: face-attendance
   License: MIT
   Space SDK: Docker  ← IMPORTANT!
   Visibility: Public
   ```
3. Click **"Create Space"**

**Done?** You'll see a blank space page. Continue to Step 3.

---

### Step 3: Get Your Token
1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `deployment`
4. Type: **Write**
5. Click **"Generate token"**
6. **Copy the token** (starts with `hf_...`)

**Done?** Continue to Step 4.

---

### Step 4: Deploy from Your Computer

Open **Command Prompt** in your project folder:

```bash
# 1. Install Hugging Face CLI
pip install huggingface_hub

# 2. Login (paste your token when asked)
huggingface-cli login

# 3. Clone your space (replace YOUR_USERNAME)
git clone https://huggingface.co/spaces/YOUR_USERNAME/face-attendance

# 4. Go into the folder
cd face-attendance

# 5. Copy files from your project
# Windows PowerShell:
Copy-Item -Path ..\backend\* -Destination backend\ -Recurse -Force
Copy-Item -Path ..\frontend\ -Destination frontend\ -Recurse -Force
Copy-Item -Path ..\Dockerfile.huggingface -Destination .
Copy-Item -Path ..\backend\requirements_minimal.txt -Destination .

# 6. Push to Hugging Face
git add .
git commit -m "First deployment"
git push
```

**Done?** Go to Step 5.

---

### Step 5: Wait for Build
1. Go to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/face-attendance`
2. Click **"App"** tab
3. Watch the build progress
4. Wait **5-10 minutes**

**Status changes:**
- 🔄 Building → ⏳ Running

---

### Step 6: Test Your App
When status shows **"Running"**:

1. You'll see your app interface
2. Click the **external link** or navigate to:
   - `/login` - Login page
   - `/attendance` - Camera test

**It works!** 🎉

---

## 🆘 Common Issues

### "Token not found"
**Fix:** Run `huggingface-cli login` again and paste token carefully.

### "Repository not found"
**Fix:** Make sure you created the Space in Step 2.

### "Permission denied"
**Fix:** Token needs **Write** permission. Create a new token.

### Build fails
**Fix:** Check logs in **App** tab → **See logs**

### Camera doesn't work
**Fix:** 
- Allow camera permissions in browser
- Use Chrome/Firefox
- Make sure you're using HTTPS (automatic on HF)

---

## ✅ Create Admin User

After app is running:

1. Go to Space → **Settings** tab
2. Scroll to **"Factory"**
3. Click **"Open Terminal"**
4. Run:

```python
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
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin created!')
    print('Login: admin@site.com / admin123')
EOF
```

---

## 🎯 Your App URL

```
https://huggingface.co/spaces/YOUR_USERNAME/face-attendance
```

**Share this link with anyone!**

---

## 💡 Tips

- **Updates:** Just `git push` again
- **Logs:** App tab → See logs
- **Terminal:** Settings → Factory → Open Terminal
- **Delete:** Settings → Scroll down → Delete space

---

## 🎉 That's It!

Your face recognition attendance system is **LIVE** on the internet!

**Next steps:**
1. Test camera on `/attendance`
2. Create admin user (see above)
3. Login and register students
4. Start marking attendance!

**Questions?** Check the logs or open a terminal in Settings.
