# Build a simple Docker image 
FROM python:3.11-slim

# Install system dependencies for SSL certificates
# This is necessary for Python to handle HTTPS requests properly.
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Default directory for the application 
WORKDIR /opt/classviz
COPY . /opt/classviz

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir jsonschema 2>/dev/null

# Container's port 
EXPOSE 7800

# Then, create the image with docker build -t classviz:latest .
