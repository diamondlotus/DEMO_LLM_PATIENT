FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements and install Python dependencies
COPY services/api_gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code and shared models
COPY services/api_gateway/ ./api_gateway/
COPY shared/ ./shared/

# Expose port
EXPOSE 8003

# Run the service
CMD ["python", "api_gateway/main.py"]
