import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Student, Attendance
from face_utils import encode_faces, recognize_faces_from_frame, save_base64_image
import cv2
import base64
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables when app context is available
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll = request.form.get('roll', '').strip()
        if not (name and roll):
            return render_template('register.html', error='Name and Roll are required')
        # check unique roll
        existing = Student.query.filter_by(roll=roll).first()
        if existing:
            return render_template('register.html', error='Roll already exists')
        student = Student(name=name, roll=roll)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('capture', roll=roll))
    return render_template('register.html')

@app.route('/capture/<roll>')
def capture(roll):
    return render_template('capture.html', roll=roll)

@app.route('/api/upload_face', methods=['POST'])
def api_upload_face():
    """
    Expects JSON: { "roll": "<roll>", "image": "data:image/jpeg;base64,..." }
    Saves the posted image into dataset/ as <roll>_<n>.jpg
    """
    data = request.get_json()
    roll = data.get('roll')
    image_b64 = data.get('image')
    if not (roll and image_b64):
        return jsonify({'error': 'missing parameters'}), 400
    saved_path = save_base64_image(image_b64, roll)
    return jsonify({'saved': os.path.basename(saved_path)})

@app.route('/train')
def train():
    data = encode_faces()
    total = len(data.get('encodings', [])) if data else 0
    return render_template('train.html', total=total)

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

@app.route('/api/start_recognize', methods=['POST'])
def api_start_recognize():
    """
    This endpoint captures a single server-webcam frame and recognizes faces.
    NOTE: For real deployments use a separate worker or client-side recognition.
    """
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        return jsonify({'error': 'camera not available'}), 500

    results = recognize_faces_from_frame(frame) if 'recognize_faces_from_frame' in globals() else recognize_faces_from_frame(frame)
    # in our face_utils the function name is recognize_faces_from_frame
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
    return jsonify({'marked': marked})

@app.route('/api/recognize_attendance', methods=['POST'])
def api_recognize_attendance():
    """
    This endpoint receives an image from the client, processes it for face recognition,
    and marks attendance for recognized students.
    """
    try:
        data = request.get_json()
        image_b64 = data.get('image')
        
        if not image_b64:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode the base64 image
        if ',' in image_b64:
            header, image_b64 = image_b64.split(',', 1)
        
        image_data = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the frame for face recognition
        results = recognize_faces_from_frame(frame)
        
        recognized = []
        for res in results:
            roll = res.get('name')
            if roll and roll != 'Unknown':
                student = Student.query.filter_by(roll=roll).first()
                if student:
                    # Check if attendance is already marked for today
                    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_att = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        Attendance.timestamp >= today_start
                    ).first()
                    
                    if not existing_att:
                        # Mark attendance for the student
                        att = Attendance(student_id=student.id)
                        db.session.add(att)
                        db.session.commit()
                        
                        recognized.append({
                            'roll': student.roll,
                            'name': student.name
                        })
                    else:
                        # Student already marked for today
                        recognized.append({
                            'roll': student.roll,
                            'name': student.name
                        })
        
        return jsonify({'recognized': recognized})
        
    except Exception as e:
        print(f"Error in attendance recognition: {str(e)}")
        return jsonify({'error': 'Recognition failed'}), 500

# small alias to ensure name resolves; try to import reliable name
try:
    from face_utils import recognize_faces_from_frame as recognize_faces_from_frame
except Exception:
    pass

@app.route('/dashboard')
def dashboard():
    students = Student.query.order_by(Student.id).all()
    attendance = Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all()
    return render_template('dashboard.html', students=students, attendance=attendance)

if __name__ == '__main__':
    app.run(debug=True)
