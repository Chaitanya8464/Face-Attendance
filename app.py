import os
import base64
import numpy as np
import cv2
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Student, Attendance
from face_utils import encode_faces, recognize_faces_from_frame, save_base64_image

# --- Flask & Database Setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Ensure tables exist ---
with app.app_context():
    db.create_all()


# -----------------------
# ROUTES
# -----------------------

@app.route('/')
def index():
    return render_template('index.html')


# -----------------------
# Register Student
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll = request.form.get('roll', '').strip()

        if not (name and roll):
            return render_template('register.html', error='Name and Roll are required')

        existing = Student.query.filter_by(roll=roll).first()
        if existing:
            return render_template('register.html', error='Roll already exists')

        student = Student(name=name, roll=roll)
        db.session.add(student)
        db.session.commit()

        return redirect(url_for('capture', roll=roll))

    return render_template('register.html')


# -----------------------
# Capture Face Photos
# -----------------------
@app.route('/capture/<roll>')
def capture(roll):
    student = Student.query.filter_by(roll=roll).first()
    if not student:
        return redirect(url_for('register'))
    return render_template('capture.html', roll=roll)


@app.route('/api/upload_face', methods=['POST'])
def api_upload_face():
    """
    Expects JSON:
    {
      "roll": "<roll>",
      "image": "data:image/jpeg;base64,..."
    }
    Saves the image to dataset/<roll>/<count>.jpg
    """
    try:
        data = request.get_json()
        roll = data.get('roll')
        image_b64 = data.get('image')

        if not (roll and image_b64):
            return jsonify({'error': 'Missing roll or image data'}), 400

        saved_path = save_base64_image(image_b64, roll)
        filename = os.path.basename(saved_path)

        return jsonify({'saved': filename}), 200

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return jsonify({'error': 'Upload failed'}), 500


# -----------------------
# Train Model (Encode Faces)
# -----------------------
@app.route('/train')
def train():
    try:
        data = encode_faces()
        total = len(data.get('encodings', [])) if data else 0
        return render_template('train.html', total=total)
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        return render_template('train.html', total=0, error="Training failed. Check dataset and face_utils.py.")


# -----------------------
# Attendance Page
# -----------------------
@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')


# -----------------------
# Real-Time Recognition (server webcam)
# -----------------------
@app.route('/api/start_recognize', methods=['POST'])
def api_start_recognize():
    """
    Captures a frame from the server webcam and recognizes faces.
    """
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()

        if not ret:
            return jsonify({'error': 'Camera not available'}), 500

        results = recognize_faces_from_frame(frame)
        marked = []

        for res in results:
            roll = res.get('name')
            if roll and roll != 'Unknown':
                student = Student.query.filter_by(roll=roll).first()
                if student:
                    att = Attendance(student_id=student.id)
                    db.session.add(att)
                    db.session.commit()
                    marked.append({'roll': student.roll, 'name': student.name})

        return jsonify({'marked': marked}), 200

    except Exception as e:
        print(f"[ERROR] Recognition failed: {e}")
        return jsonify({'error': 'Recognition failed'}), 500


# -----------------------
# Client Image Recognition (browser upload)
# -----------------------
@app.route('/api/recognize_attendance', methods=['POST'])
def api_recognize_attendance():
    """
    Receives a base64 image from the client, recognizes faces, and marks attendance.
    """
    try:
        data = request.get_json()
        image_b64 = data.get('image')

        if not image_b64:
            return jsonify({'error': 'No image provided'}), 400

        # Decode base64
        if ',' in image_b64:
            image_b64 = image_b64.split(',', 1)[1]
        image_data = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        results = recognize_faces_from_frame(frame)
        recognized = []

        for res in results:
            roll = res.get('name')
            if roll and roll != 'Unknown':
                student = Student.query.filter_by(roll=roll).first()
                if student:
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_att = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.timestamp >= today_start
                    ).first()

                    if not existing_att:
                        att = Attendance(student_id=student.id)
                        db.session.add(att)
                        db.session.commit()

                    recognized.append({
                        'roll': student.roll,
                        'name': student.name
                    })

        return jsonify({'recognized': recognized}), 200

    except Exception as e:
        print(f"[ERROR] Attendance recognition failed: {e}")
        return jsonify({'error': 'Recognition failed'}), 500


# -----------------------
# Dashboard Page
# -----------------------
@app.route('/dashboard')
def dashboard():
    students = Student.query.order_by(Student.id).all()
    attendance = Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all()
    return render_template('dashboard.html', students=students, attendance=attendance)


# -----------------------
# MAIN ENTRY
# -----------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
