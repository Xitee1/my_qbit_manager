# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --user .

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create logs directory
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Set non-root user for security
RUN useradd -m -u 1000 qbitmanager && \
    chown -R qbitmanager:qbitmanager /app

USER qbitmanager

# Health check
HEALTHCHECK --interval=5m --timeout=3s \
    CMD python -c "import sys; sys.exit(0)"

# Default entrypoint - can be overridden for different service modes
ENTRYPOINT ["python", "-m", "my_qbit_manager.main"]

# Default command - run in scheduler mode
CMD ["--mode", "scheduler"]
