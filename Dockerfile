# Face Attendance System Dockerfile for Render
# This Dockerfile is optimized for Render's build context

FROM python:3.11-slim

# Limit parallel compilation to reduce memory usage
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements first (better caching)
COPY backend/requirements.txt .

# Install dependencies in stages
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
        gunicorn==21.2.0 \
        psycopg2-binary==2.9.9

# Copy backend code
COPY backend/ ./backend/

# Copy frontend code
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/backend/dataset /app/backend/instance

# Set environment variables
ENV FLASK_APP=backend/app/app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "backend.app.app:app"]
