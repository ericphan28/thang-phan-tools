# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ONLY runtime dependencies (no dev tools)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
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
COPY requirements-prod.txt .

# Install Python dependencies (production only) with pip cache
# NOTE: Do NOT use --no-cache-dir here, otherwise the BuildKit pip cache mount is ineffective.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-prod.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/models /app/temp /app/logs

# Expose port
EXPOSE 8000

# Health check (matches app.main_simple)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read(); print('ok')" || exit 1

# Run the application
# Note: the project entrypoint is app.main_simple:app (includes all routers like /api/v1/ai-admin)
CMD ["uvicorn", "app.main_simple:app", "--host", "0.0.0.0", "--port", "8000"]
