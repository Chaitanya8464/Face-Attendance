# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add email notifications for low attendance
- Implement bulk student import via CSV
- Add student profile pages with photos
- Class/section management
- Holiday and leave management

### In Progress
- Improving face recognition accuracy with multiple angles
- Adding confidence scores to recognition results

## [1.2.0] - 2025-02-15

### Added
- Dark mode toggle with localStorage persistence
- CSV export functionality for attendance records
- Student deletion with confirmation modal
- Attendance filters (All/Today/This Week)
- Search functionality in dashboard
- Toast notification system
- Confetti celebration effects

### Changed
- Complete UI redesign with modern gradient theme
- Improved responsive design for mobile devices
- Enhanced animations and transitions
- Updated Bootstrap to 5.3.2
- Upgraded to Chart.js 4.4.0

### Fixed
- Fixed duplicate attendance entries for same day
- Improved camera handling on mobile browsers
- Fixed navbar active state highlighting

## [1.1.0] - 2024-12-10

### Added
- Health check endpoint for Railway deployment
- Render deployment configuration (render.yaml)
- Railway deployment fixes
- Environment variable support for PORT and FLASK_ENV

### Changed
- Updated requirements.txt with compatible versions
- Improved error handling in face recognition
- Enhanced logging for debugging

### Fixed
- Fixed encoding file not found error
- Resolved database connection issues on Render
- Fixed camera permission handling

## [1.0.0] - 2024-11-20

### Added
- Initial release
- Student registration system
- Face capture and encoding
- Face recognition for attendance
- Basic dashboard with attendance records
- Training endpoint for face encoding
- SQLite database with SQLAlchemy ORM
- Docker support for deployment
- README documentation

### Known Issues
- First recognition attempt may fail occasionally
- Large datasets may cause slow training times
- SQLite may have concurrency issues under heavy load

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.2.0 | 2025-02-15 | UI overhaul, dark mode, export features |
| 1.1.0 | 2024-12-10 | Deployment improvements |
| 1.0.0 | 2024-11-20 | Initial release |

## Notes

- Face recognition uses dlib's 128-dimensional face embeddings
- Default recognition threshold is 0.6 (can be adjusted in face_utils.py)
- Images are processed at 1/4 scale for performance
- Encodings are cached in encodings.pkl for faster recognition
