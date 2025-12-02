# Use official Python image
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Install system deps (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

# Make start script executable
RUN chmod +x /app/scripts/start.sh

# Use a non-root user for safety
RUN useradd --create-home appuser || true
USER appuser

# Default command
CMD ["/app/scripts/start.sh"]
