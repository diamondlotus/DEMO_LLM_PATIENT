FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements and install Python dependencies
COPY services/api_gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copy service code and shared models
COPY services/api_gateway/ ./api_gateway/
=======
# Copy service and shared code
COPY services/ ./services/
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a
COPY shared/ ./shared/

# Expose port
EXPOSE 8003

# Run the service
CMD ["python", "services/api_gateway/main.py"]
