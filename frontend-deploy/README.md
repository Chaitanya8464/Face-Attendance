# Face Attendance System - Frontend Deployment

This directory contains the standalone frontend for the Face Attendance System. It can be deployed independently without the backend.

## Directory Structure

```
frontend-deploy/
├── index.html      # Main HTML file
├── css/
│   └── styles.css  # All styles
├── js/
│   ├── main.js     # Main JavaScript
│   └── camera.js   # Camera utilities
├── images/         # Place your images here
└── README.md       # This file
```

## Deployment Options

### Option 1: Static Hosting (Recommended)

Upload the entire `frontend-deploy` folder to any static hosting service:

- **Netlify**: Drag and drop the folder to [netlify.com/drop](https://app.netlify.com/drop)
- **Vercel**: Run `vercel deploy` in this directory
- **GitHub Pages**: Push to a GitHub repository and enable Pages
- **Firebase Hosting**: Use `firebase deploy`

### Option 2: Local Testing

Simply open `index.html` in your browser:

```bash
# Windows
start index.html

# Mac
open index.html

# Linux
xdg-open index.html
```

### Option 3: Simple HTTP Server

For local testing with proper HTTP server:

```bash
# Python 3
python -m http.server 8000

# Node.js (npx)
npx http-server -p 8000

# PHP
php -S localhost:8000
```

Then visit: `http://localhost:8000`

## Features Included

✅ Responsive design (mobile, tablet, desktop)
✅ Dark/Light mode toggle
✅ Smooth animations and transitions
✅ Bootstrap 5.3.2 via CDN
✅ Font Awesome 6.4.0 via CDN
✅ Chart.js 4.4.0 via CDN

## Customization

### Change Colors

Edit `css/styles.css` and modify the CSS variables:

```css
:root {
  --primary-color: #4a4a4a;
  --success-color: #2d2d2d;
  --light-bg: #D6D5D1;
  --dark-bg: #161616;
}
```

### Add Your Logo

Replace the navbar brand in `index.html`:

```html
<a class="navbar-brand" href="#">
  <img src="images/logo.png" alt="Logo" height="40">
  <span>Your Brand</span>
</a>
```

## Notes

- This is a **frontend-only** deployment
- Backend features (face recognition, database) require the full application
- CDN resources require internet connection
- For offline use, download Bootstrap and Font Awesome locally

## License

Same as the main project license.
