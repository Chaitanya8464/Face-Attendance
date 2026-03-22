# Frontend - Face Recognition Attendance System

This directory contains the frontend templates and static assets for the face recognition attendance system.

## Directory Structure

```
frontend/
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template with common layout
│   ├── index.html      # Landing page
│   ├── attendance.html # Attendance view
│   ├── capture.html    # Face capture interface
│   ├── train.html      # Training interface
│   ├── dashboard.html  # General dashboard
│   ├── dashboard_admin.html
│   ├── dashboard_teacher.html
│   ├── dashboard_student.html
│   ├── register.html   # Student registration
│   ├── auth/           # Authentication templates
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── forgot_password.html
│   │   ├── reset_password.html
│   │   ├── verify_email.html
│   │   └── student_login.html
│   ├── admin/          # Admin panel templates
│   ├── teacher/        # Teacher panel templates
│   ├── student/        # Student panel templates
│   └── emails/         # Email templates
└── static/             # Static assets
    ├── css/
    │   └── styles.css  # Main stylesheet
    └── js/
        ├── main.js     # Main JavaScript
        └── camera.js   # Camera handling for face capture
```

## Technologies

- **HTML5** - Structure and markup
- **CSS3** - Styling and layout
- **JavaScript (Vanilla)** - Client-side interactivity
- **Jinja2** - Server-side templating (rendered by Flask)

## Template Hierarchy

```
base.html (extends by all pages)
├── index.html (landing page)
├── auth/ (authentication pages)
│   ├── login.html
│   ├── signup.html
│   └── ...
├── dashboard*.html (role-based dashboards)
├── student/ (student-specific pages)
├── teacher/ (teacher-specific pages)
└── admin/ (admin-specific pages)
```

## Static Assets

### CSS
- `styles.css` - Contains all custom styles
- Uses responsive design with mobile-first approach
- Includes utility classes for common patterns

### JavaScript
- `main.js` - General UI interactions and utilities
- `camera.js` - WebRTC camera access for face capture

## Customization

### Changing Styles
Edit `static/css/styles.css` to modify:
- Color scheme
- Layout and spacing
- Component styles
- Responsive breakpoints

### Adding New Pages
1. Create new HTML file in `templates/` or appropriate subdirectory
2. Extend `base.html` using Jinja2 template inheritance
3. Add route in backend `app/app.py`
4. Link static assets if needed

### Modifying Layout
Edit `templates/base.html` to change:
- Navigation structure
- Footer content
- Common scripts and styles
- Meta tags and SEO

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Note:** Camera functionality requires HTTPS in production (except localhost).

## Integration with Backend

The frontend is tightly coupled with the Flask backend:
- Templates are rendered server-side using Jinja2
- Static files are served by Flask
- Forms submit to Flask routes
- Flash messages are displayed from backend

## Development Tips

1. **Template Debugging:** Enable Flask debug mode to see template changes instantly
2. **Static Files:** Hard refresh (Ctrl+F5) to bypass cache during development
3. **Camera Testing:** Test camera functionality in a secure context (HTTPS or localhost)

## Notes

- This frontend is server-side rendered (not a SPA)
- All dynamic behavior is handled through Flask routes
- No build step required - changes are reflected immediately
