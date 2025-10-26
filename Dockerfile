# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libgomp1 \
    libgthread-2.0-0 \
    espeak-ng \
    libgtk2.0-dev \
    libgtk-3-dev \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies one by one to handle conflicts
RUN pip install --no-cache-dir --upgrade pip

# Install basic dependencies first
RUN pip install --no-cache-dir numpy==1.24.3

# Install OpenCV
RUN pip install --no-cache-dir opencv-python==4.8.1.78

# Install TTS
RUN pip install --no-cache-dir pyttsx3==2.90

# Install Flask (simpler than FastAPI for this use case)
RUN pip install --no-cache-dir flask==2.3.3

# Install MediaPipe (may have conflicts, install last)
RUN pip install --no-cache-dir mediapipe==0.10.5

# Install TensorFlow (largest, install last)
RUN pip install --no-cache-dir tensorflow==2.13.0

# Copy all application files
COPY . .

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/status')" || exit 1

# Run the Flask application
CMD ["python", "web_app.py"]