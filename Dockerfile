FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    procps \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code (monorepo services and shared)
COPY ./services ./services
COPY ./shared ./shared
COPY ./frontend ./frontend

# Copy nginx configurations
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx_minimal.conf /etc/nginx/nginx_minimal.conf

# Create startup scripts
COPY start.sh ./start.sh
COPY start_simple.sh ./start_simple.sh
COPY start_debug.sh ./start_debug.sh
RUN chmod +x ./start.sh ./start_simple.sh ./start_debug.sh

# Create nginx log directory
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 8000 80

# Start both nginx and the API (using simple script)
CMD ["./start_simple.sh"]

