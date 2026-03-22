# Face Attendance System Dockerfile
# Optimized for Render/Railway deployment
# 
# NOTE: Build time is ~10-15 minutes due to dlib compilation
# First build downloads and compiles dlib from source

FROM python:3.11-slim

# Limit parallel compilation to reduce memory usage during build
# This prevents OOM errors on free tier hosting
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"

# Install only essential system dependencies
# We need: git (for some packages), cmake (for dlib), build-essential (compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY requirements.txt .

# Install dependencies in stages to reduce memory pressure
# Order matters: numpy first, then dlib (slowest), then everything else
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        numpy==1.26.2 \
        pillow==10.0.1 \
        opencv-python-headless==4.7.0.72 && \
    pip install --no-cache-dir \
        dlib==19.24.2 && \
    pip install --no-cache-dir \
        face_recognition==1.3.0 \
        flask==2.3.2 \
        flask_sqlalchemy==3.0.3 \
        Werkzeug==2.3.7 \
        gunicorn==21.2.0

# Copy application code
# .dockerignore excludes dataset/, database.db, etc.
COPY . .

# Create necessary directories
RUN mkdir -p /app/backend/dataset /app/backend/instance /app/backend/faces_known

# Environment variables
ENV FLASK_APP=app/app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Gunicorn configuration:
# --timeout 120: Allow longer requests (face encoding can be slow)
# --workers 1: Single worker for SQLite compatibility
# Increase workers if using PostgreSQL
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "app.app:app"]