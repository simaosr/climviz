# Use python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
    gcc \
    gfortran \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8050

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8050/ || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "climviz.app:server"]