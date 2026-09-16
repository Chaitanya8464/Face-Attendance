"""
Face Recognition Utilities

This module handles all face-related operations:
- Encoding faces from images
- Recognizing faces in frames
- Saving uploaded images

Dependencies:
- face_recognition (built on dlib)
- opencv-python
- pickle for caching encodings

NOTE: The face_recognition library requires dlib which needs CMake to compile.
      See README.md for installation instructions.
"""
import os
import face_recognition
import cv2
import pickle
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from models import db, Student

# Directory to save captured face images
DATASET_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dataset')
ENCODINGS_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'encodings.pkl')

# Create dataset directory if it doesn't exist
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

def save_base64_image(base64_string, roll):
    """
    Saves a base64 image string to the dataset directory.
    
    Args:
        base64_string: The base64 encoded image (may include data URI prefix)
        roll: Student roll number used in filename
        
    Returns:
        Path to saved image or None if failed
        
    TODO: Add image validation (check if it's actually an image)
    TODO: Resize large images to save space
    """
    # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
    if ',' in base64_string:
        header, base64_string = base64_string.split(',', 1)

    try:
        # Decode base64 to image bytes
        image_data = base64_string.encode('utf-8')
        image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Count existing images for this roll to determine the next filename
        # Format: {roll}_1.jpg, {roll}_2.jpg, etc.
        count = len([f for f in os.listdir(DATASET_DIR) if f.startswith(f"{roll}_")])
        filename = f"{roll}_{count + 1}.jpg"
        save_path = os.path.join(DATASET_DIR, filename)

        # Convert to RGB (if necessary) and save
        # This handles PNGs with transparency and other formats
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(save_path)

        return save_path
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def encode_faces():
    known_face_encodings = []
    known_face_rolls = []

    all_students = Student.query.all()

    for student in all_students:
        roll = student.roll
        student_encodings = []
        student_images = [f for f in os.listdir(DATASET_DIR) if f.startswith(f"{roll}_")]

        for image_file in student_images:
            image_path = os.path.join(DATASET_DIR, image_file)
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                encodings = face_recognition.face_encodings(image, face_locations)
                if encodings:
                    encoding = encodings[0]
                    student_encodings.append(encoding)

        if student_encodings:
            average_encoding = np.mean(student_encodings, axis=0)
            student.face_encoding = average_encoding
            db.session.add(student)
            known_face_encodings.append(average_encoding)
            known_face_rolls.append(roll)

    db.session.commit()

    data = {"encodings": known_face_encodings, "rolls": known_face_rolls}
    with open(ENCODINGS_FILE, "wb") as f:
        f.write(pickle.dumps(data))

    return data

def load_encodings():
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.loads(f.read())
            return data["encodings"], data["rolls"]
    except FileNotFoundError:
        print("Encodings file not found. Run /train first.")
        return [], []

def recognize_faces_from_frame(frame):
    
    known_encodings, known_rolls = load_encodings()

    if not known_encodings:
        return []

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    recognized_results = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index] and face_distances[best_match_index] < 0.6:
            name = known_rolls[best_match_index]

        top, right, bottom, left = [coord * 4 for coord in face_location]

        recognized_results.append({
            'name': name,
            'box': (top, right, bottom, left)
        })

    return recognized_results