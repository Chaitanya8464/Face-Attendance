# 📷 Camera Quick Reference

## 🔍 Quick Diagnosis (2 minutes)

### Step 1: Check URL
```
✅ http://localhost:8000     - Should work
✅ https://yourdomain.com     - Should work  
❌ http://192.168.1.100:8000 - Won't work (needs HTTPS)
```

### Step 2: Run Camera Test
```
Visit: http://localhost:8000/camera-test
Click: "Run All Tests"
```

### Step 3: Check Browser Console
```
Press: F12
Look for: Red error messages
```

---

## ⚡ Common Fixes

### "Camera access denied"
1. Click lock icon in address bar
2. Change Camera permission to "Allow"
3. Refresh page

### "No camera found"
1. Connect camera
2. Close Zoom/Teams
3. Test in Windows Camera app

### "Security error"
1. Use `localhost` not IP address
2. Or set up HTTPS

### "Upload failed"
1. Check Flask console logs
2. Verify `backend/dataset/` exists
3. Check disk space

---

## 🛠️ Quick Commands

### Test Camera Page
```
http://localhost:8000/camera-test
```

### Start Server
```bash
cd backend
python app/app.py
```

### Check Logs
```bash
# Server logs show in terminal where Flask is running
# Look for [INFO], [ERROR], [WARNING] messages
```

---

## 📋 Error Quick Reference

| Error | Fix |
|-------|-----|
| NotAllowedError | Allow camera in browser |
| NotFoundError | Connect camera |
| NotReadableError | Close other apps |
| SecurityError | Use HTTPS/localhost |

---

## 🔧 Browser Settings

### Chrome
```
Settings → Privacy → Site Settings → Camera
Add: http://localhost:8000 → Allow
```

### Firefox
```
Settings → Privacy → Permissions → Camera → Settings
Allow: http://localhost:8000
```

### Edge
```
Settings → Cookies → Camera
Allow: http://localhost:8000
```

---

## 🚨 Emergency Checklist

If nothing works:

- [ ] Restart browser
- [ ] Clear cache (Ctrl+Shift+Delete)
- [ ] Try different browser (Chrome recommended)
- [ ] Check camera in Windows Camera app
- [ ] Restart Flask server
- [ ] Check `backend/dataset/` folder exists
- [ ] Verify Python dependencies installed

---

## 📞 Getting Help

1. **Run diagnostics:**
   ```
   http://localhost:8000/camera-test
   ```

2. **Collect logs:**
   - Browser console (F12)
   - Flask server terminal

3. **Check documentation:**
   - `CAMERA_TROUBLESHOOTING.md` - Detailed guide
   - `CAMERA_FIXES.md` - What was fixed

---

## ✅ Success Indicators

Camera working:
- ✅ Green "Active" status
- ✅ Video shows in player
- ✅ No console errors
- ✅ Can capture photos
- ✅ Upload returns success

---

**Need more help?** See `CAMERA_TROUBLESHOOTING.md` for detailed guide.
