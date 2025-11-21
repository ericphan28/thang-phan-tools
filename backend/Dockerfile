# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ONLY runtime dependencies (no dev tools)
RUN apt-get update && apt-get install -y \
    # OpenCV runtime dependencies
    libsm6 \
    libxext6 \
    libgomp1 \
    libglib2.0-0 \
    libglvnd0 \
    libgl1 \
    # Tesseract OCR (runtime only)
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-vie \
    # PDF processing (runtime only)
    poppler-utils \
    # Image conversion
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir email-validator==2.1.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/models /app/temp /app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
