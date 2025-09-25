# Dockerfile for Production Deployment
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed output logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for health checks
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "src/scheduler.py", "--daemon"]