# Use Python 3.10 slim image with additional CA certificates
FROM python:3.10-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0 \
    # Disable IPv6
    NETWORK_IPV6=no \
    # Optimize DNS resolution
    RES_OPTIONS="rotate timeout:1 attempts:1"

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
WORKDIR /app
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE $PORT

# Health check with connection test
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://$HOST:$PORT/health || exit 1

# Make run.py executable
RUN chmod +x run.py

# Set default command with proper signal handling
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--timeout", "120", "--keep-alive", "60", "app.main:app"]

# Add custom DNS configuration
RUN echo "options single-request" >> /etc/resolv.conf && \
    echo "options timeout:1" >> /etc/resolv.conf && \
    echo "options attempts:1" >> /etc/resolv.conf