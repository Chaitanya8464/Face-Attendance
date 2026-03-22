# Face Attendance System Dockerfile for Render
# Optimized for low-memory environments

FROM python:3.11-slim

# Set memory limits for compilation
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install in stages to reduce memory pressure
# Stage 1: Basic packages
RUN pip install --no-cache-dir --upgrade pip

# Stage 2: numpy (required by dlib)
RUN pip install --no-cache-dir numpy==1.26.2

# Stage 3: dlib (most memory-intensive)
# Use specific version that compiles better
RUN pip install --no-cache-dir dlib==19.24.0

# Stage 4: face_recognition (depends on dlib)
RUN pip install --no-cache-dir face_recognition==1.3.0

# Stage 5: Other packages
RUN pip install --no-cache-dir \
    pillow==10.0.1 \
    opencv-python-headless==4.7.0.72 \
    flask==2.3.2 \
    flask_sqlalchemy==3.0.3 \
    Werkzeug==2.3.7 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.9

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/backend/dataset /app/backend/instance

# Set environment variables
ENV FLASK_APP=backend/app/app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "backend.app.app:app"]
