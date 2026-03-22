# Camera Troubleshooting Guide

## Common Camera Issues and Solutions

### Issue 1: "Camera access denied" or "getUserMedia not supported"

**Cause:** Browser security requirements

**Solutions:**

1. **Use HTTPS or localhost**
   - Modern browsers require HTTPS for camera access in production
   - For development, `http://localhost:8000` works fine
   - If accessing via IP address (e.g., `http://192.168.1.100:8000`), camera will be blocked

2. **Check browser permissions**
   - Chrome: Click the lock icon in address bar → Site settings → Camera → Allow
   - Firefox: Click the camera icon in address bar → Allow
   - Edge: Click the lock icon → Permissions → Camera → Allow

3. **Browser compatibility**
   - Use Chrome, Firefox, or Edge (latest versions)
   - Safari requires HTTPS even for localhost in some versions

### Issue 2: "Camera not available" or black screen

**Cause:** Camera hardware or driver issues

**Solutions:**

1. **Check if camera is being used by another application**
   - Close Zoom, Teams, or other video applications
   - Only one application can use the camera at a time

2. **Test camera in another application**
   - Open Windows Camera app to verify hardware works
   - Try camera in Google Meet or similar

3. **Update camera drivers**
   - Device Manager → Cameras → Right-click → Update driver

### Issue 3: Camera works but face recognition fails

**Cause:** Backend processing issues

**Solutions:**

1. **Check if face_recognition library is installed**
   ```bash
   pip list | grep face_recognition
   ```

2. **Verify dataset directory exists**
   - Should be at: `backend/dataset/`
   - Check permissions: The Flask app needs write access

3. **Check encodings.pkl file**
   - Should be at: `backend/encodings.pkl`
   - Delete and retrain if corrupted

4. **Test with better lighting**
   - Ensure face is well-lit
   - Avoid backlighting (windows behind you)
   - Face the camera directly

### Issue 4: Upload failed errors

**Cause:** Server-side processing errors

**Debugging Steps:**

1. **Check Flask console logs**
   - Look for `[ERROR]` messages
   - Common issues: Missing dependencies, permission errors

2. **Verify JSON payload**
   - Open browser DevTools → Network tab
   - Check the request payload to `/api/upload_face`
   - Should contain: `{"roll": "...", "image": "data:image/..."}`

3. **Check server storage**
   - Ensure disk space is available
   - Verify `backend/dataset/` directory is writable

## Development Mode Testing

### Test Camera Separately

Create a test page at `backend/app/test_camera.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Camera Test</title>
</head>
<body>
    <h1>Camera Test</h1>
    <video id="video" autoplay playsinline style="width: 640px; height: 480px;"></video>
    <button id="testBtn">Test Camera</button>
    <div id="status"></div>

    <script>
        document.getElementById('testBtn').onclick = async () => {
            const status = document.getElementById('status');
            const video = document.getElementById('video');

            try {
                status.textContent = 'Requesting camera access...';
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                status.textContent = '✅ Camera working!';
                status.style.color = 'green';
            } catch (err) {
                status.textContent = '❌ Error: ' + err.message;
                status.style.color = 'red';
                console.error('Camera error:', err);
            }
        };
    </script>
</body>
</html>
```

### Test Backend API

Use curl or Postman to test `/api/upload_face`:

```bash
# Test with a sample image
curl -X POST http://localhost:8000/api/upload_face \
  -H "Content-Type: application/json" \
  -d "{\"roll\": \"TEST001\", \"image\": \"data:image/jpeg;base64,/9j/4AAQSkZJRg...\"}"
```

## Production Deployment

### HTTPS Setup

**Option 1: Let's Encrypt (Free)**
```bash
# On your server
certbot --nginx -d yourdomain.com
```

**Option 2: Cloudflare**
- Use Cloudflare's free SSL/TLS
- Point your domain to Cloudflare
- Enable "Always Use HTTPS"

**Option 3: Reverse Proxy with Nginx**
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker with HTTPS

```yaml
# docker-compose.yml
version: '3'
services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
```

## Quick Diagnostic Script

Run this in browser console to check camera support:

```javascript
(async () => {
    console.log('🔍 Camera Diagnostic Test');

    // Check API support
    if (!navigator.mediaDevices) {
        console.error('❌ navigator.mediaDevices not available');
        console.log('💡 Try using HTTPS or localhost');
        return;
    }

    if (!navigator.mediaDevices.getUserMedia) {
        console.error('❌ getUserMedia not supported');
        return;
    }

    console.log('✅ getUserMedia supported');

    // Check permissions
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        console.log('✅ Camera access granted');

        // Stop the stream
        stream.getTracks().forEach(track => track.stop());
        console.log('✅ Camera test completed successfully');
    } catch (err) {
        console.error('❌ Camera access failed:', err.message);
        console.log('💡 Check browser permissions and HTTPS');
    }
})();
```

## Error Messages Reference

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `NotAllowedError` | Permission denied | Allow camera in browser settings |
| `NotFoundError` | No camera found | Connect camera, check drivers |
| `NotReadableError` | Camera in use | Close other apps using camera |
| `OverconstrainedError` | Resolution not supported | Lower resolution requirements |
| `TypeError` | API not supported | Use HTTPS or localhost |
| `SecurityError` | Cross-origin issue | Same-origin policy violation |
