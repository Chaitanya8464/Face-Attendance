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
    """
    Computes face encodings for all students and saves them.
    
    Process:
    1. Finds all face images in the 'dataset' directory
    2. Computes the 128-D face encoding for each face
    3. Averages multiple encodings per student (if multiple images exist)
    4. Saves the encoding to the Student table in the database
    5. Also saves a pickled version of all encodings for quick lookup
    
    Returns:
        Dictionary with 'encodings' and 'rolls' lists
        
    NOTE: This function is called when user clicks "Train" in the UI.
          For large datasets, consider background processing with Celery.
    """
    known_face_encodings = []
    known_face_rolls = []

    # Process images and update database
    all_students = Student.query.all()

    for student in all_students:
        roll = student.roll
        student_encodings = []

        # Find all images for this student's roll
        # Naming convention: {roll}_1.jpg, {roll}_2.jpg, etc.
        student_images = [f for f in os.listdir(DATASET_DIR) if f.startswith(f"{roll}_")]

        for image_file in student_images:
            image_path = os.path.join(DATASET_DIR, image_file)
            image = face_recognition.load_image_file(image_path)

            # Find the face encoding in the image
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                encodings = face_recognition.face_encodings(image, face_locations)
                if encodings:
                    # For simplicity, we only save the first face found in the first image.
                    # In a robust system, you'd average encodings or use multiple.
                    encoding = encodings[0]
                    student_encodings.append(encoding)

        if student_encodings:
            # Use the average encoding if multiple images were captured, otherwise use the single one
            # This improves recognition accuracy
            average_encoding = np.mean(student_encodings, axis=0)

            # Save the average encoding to the database
            student.face_encoding = average_encoding
            db.session.add(student)

            # Add to temporary lists for the pickle file
            known_face_encodings.append(average_encoding)
            known_face_rolls.append(roll)

    db.session.commit()

    # Save a cached version of all encodings to a pickle file for fast retrieval
    # This avoids recomputing encodings on every recognition request
    data = {"encodings": known_face_encodings, "rolls": known_face_rolls}
    with open(ENCODINGS_FILE, "wb") as f:
        f.write(pickle.dumps(data))

    return data

def load_encodings():
    """
    Loads the pre-computed encodings from the pickle file.
    
    Returns:
        Tuple of (encodings_list, rolls_list) or ([], []) if file not found
        
    NOTE: If encodings file is missing, run /train endpoint first.
    """
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.loads(f.read())
            return data["encodings"], data["rolls"]
    except FileNotFoundError:
        print("Encodings file not found. Run /train first.")
        return [], []

def recognize_faces_from_frame(frame):
    """
    Recognizes faces in a single OpenCV frame (numpy array).
    
    Args:
        frame: OpenCV image (BGR format)
        
    Returns:
        List of dicts with 'name' (roll) and 'box' (bounding box) for each face
        
    How it works:
    1. Load known encodings from pickle cache
    2. Resize frame to 1/4 size for faster processing
    3. Detect faces and compute encodings
    4. Compare with known faces using Euclidean distance
    5. Match if distance < 0.6 (threshold can be adjusted)
    
    Performance:
        - Processing at 1/4 scale for speed (4x faster)
        - Consider using GPU acceleration for production
        
    TODO: Add confidence score to results
    TODO: Handle multiple faces better (currently returns all)
    """
    # Load known encodings (the "trained" data)
    known_encodings, known_rolls = load_encodings()

    if not known_encodings:
        return []

    # Resize frame for faster processing (optional)
    # 1/4 scale is a good balance between speed and accuracy
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    recognized_results = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Compare current face with known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        # A threshold of 0.6 is common, meaning faces closer than 0.6 are a match
        # Lower = stricter matching, Higher = more lenient
        if matches[best_match_index] and face_distances[best_match_index] < 0.6:
            name = known_rolls[best_match_index]

        # Rescale face location back to full frame size
        # (we multiplied by 4 because we divided by 4 earlier)
        top, right, bottom, left = [coord * 4 for coord in face_location]

        recognized_results.append({
            'name': name,
            'box': (top, right, bottom, left)
        })

    return recognized_results