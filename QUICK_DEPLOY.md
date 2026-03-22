# ⚡ Quick Deploy Checklist

## 5-Minute Deployment (Railway - Easiest)

### Prerequisites (2 min)
- [ ] GitHub account created
- [ ] Railway account created (https://railway.app)
- [ ] Code pushed to GitHub

### Deployment Steps (3 min)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Click "Deploy"

3. **Configure**
   - Go to Variables tab
   - Add: `SECRET_KEY=any-random-32-character-string`
   - Add: `FLASK_ENV=production`

4. **Done!**
   - Railway provides free URL: `https://your-app.up.railway.app`
   - HTTPS enabled automatically
   - Wait 10-15 minutes for first build (dlib compilation)

---

## 10-Minute Deployment (Render - Production Ready)

### Prerequisites (2 min)
- [ ] GitHub account
- [ ] Render account (https://render.com)
- [ ] Code on GitHub

### Deployment Steps (8 min)

1. **Update render.yaml** (already done ✅)
   - File exists in project root
   - Configures web service + PostgreSQL

2. **Deploy on Render**
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect GitHub repository
   - Select `render.yaml`
   - Click "Apply"

3. **Wait for Build**
   - Takes 15-20 minutes (dlib compilation)
   - Monitor in Deployments tab

4. **Create Admin User**
   - Go to Shell in Render dashboard
   - Run:
   ```bash
   cd backend
   python -c "from app import app,db,User; 
   app.app_context().push(); 
   admin=User(email='admin@yoursite.com',username='admin',role='admin',is_verified=True); 
   admin.set_password('change-me'); 
   db.session.add(admin); 
   db.session.commit()"
   ```

5. **Done!**
   - URL: `https://your-app.onrender.com`
   - PostgreSQL database auto-created
   - Free SSL certificate

---

## 2-Minute Deployment (Hugging Face - Demo Only)

### For Quick Testing

1. **Install HF CLI**
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```

2. **Create Space**
   - Go to https://huggingface.co/new-space
   - Name: `attendance-demo`
   - SDK: Docker
   - Visibility: Public

3. **Deploy**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/attendance-demo
   cp -r backend/* attendance-demo/
   cp Dockerfile.huggingface attendance-demo/Dockerfile
   cd attendance-demo
   git add .
   git commit -m "Deploy"
   git push
   ```

4. **Done!**
   - URL: `https://huggingface.co/spaces/YOUR_USERNAME/attendance-demo`
   - ⚠️ Public and resets on redeploy

---

## Post-Deployment (All Platforms)

### Immediate Actions
- [ ] Visit your deployed URL
- [ ] Test `/health` endpoint
- [ ] Login with admin credentials
- [ ] Create admin user (if not done)

### Within 24 Hours
- [ ] Change admin password immediately
- [ ] Configure email settings (optional)
- [ ] Test camera access (requires HTTPS)
- [ ] Register a test student

### Optional Configuration
```env
# Email (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security
SECRET_KEY=<generate-random-32-chars>

# Database (if not using auto-configured)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## Common Issues & Quick Fixes

### Build Fails
```
Error: npm ERR! or Memory error
Fix: Wait 5 minutes, retry build
```

### Camera Not Working
```
Issue: HTTP instead of HTTPS
Fix: All platforms provide HTTPS automatically
     Make sure you use the https:// URL
```

### Database Errors
```
Issue: SQLite not persisting
Fix: Use PostgreSQL (Render) or external DB
```

### 404 on /signup
```
Note: Expected - signup page was removed
Use: Admin creates accounts instead
```

---

## URLs to Remember

| Platform | Dashboard | Docs |
|----------|-----------|------|
| Railway | https://railway.app | https://docs.railway.app |
| Render | https://render.com | https://render.com/docs |
| Hugging Face | https://huggingface.co/spaces | https://huggingface.co/docs/hub/spaces |

---

## Cost Breakdown

### Railway
- Free: 500 hours/month (~$5 credit)
- Enough for: Continuous uptime for 20 days
- Overage: $0.0005/minute

### Render
- Free: 750 hours/month
- Enough for: Continuous uptime all month
- Database: Free 1GB PostgreSQL included

### Hugging Face
- Free: Unlimited
- Limitations: Public repos only, no persistent storage

---

## Next Steps After Deployment

1. **Test Core Features**
   - Login/Logout
   - Register student
   - Capture faces
   - Train model
   - Mark attendance

2. **Monitor Performance**
   - Check platform dashboard
   - Monitor build logs
   - Watch for sleep/wake cycles

3. **Configure Custom Domain** (Optional)
   - Railway: Settings → Domains
   - Render: Dashboard → Custom Domain
   - Both provide free SSL

4. **Set Up Monitoring** (Optional)
   - Uptime monitoring: https://uptimerobot.com (free)
   - Error tracking: https://sentry.io (free tier)

---

**Need more help?** See `DEPLOYMENT_FREE.md` for detailed guides.
