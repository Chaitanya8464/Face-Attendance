FROM python:3.11-slim

# Limit parallel compilation to reduce memory usage
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS="-j1"

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies in stages to reduce memory pressure
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

COPY . .

RUN mkdir -p /app/dataset /app/instance /app/faces_known

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "app:app"]