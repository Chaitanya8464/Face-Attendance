# Face Attendance System Dockerfile
# Uses pre-built dlib to avoid compilation timeout

FROM ghcr.io/justadudewhohacks/face_recognition:latest

# Set working directory
WORKDIR /app

# Install additional system packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (excluding dlib and face_recognition)
COPY backend/requirements_minimal.txt .
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create directories
RUN mkdir -p /app/backend/dataset /app/backend/instance /app/backend/faces_known

# Environment variables
ENV FLASK_APP=backend/app/app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "backend.app.app:app"]
