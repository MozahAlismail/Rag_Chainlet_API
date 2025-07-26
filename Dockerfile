# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for model caching
RUN mkdir -p /tmp/huggingface /tmp/transformers /tmp/torch

# Set environment variables
ENV HUGGINGFACE_HUB_CACHE=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/transformers
ENV TORCH_HOME=/tmp/torch
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Start the application
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port $PORT"]
