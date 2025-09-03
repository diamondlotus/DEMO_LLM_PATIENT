FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements and install Python dependencies
COPY services/auth_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code, shared models, and database
COPY services/auth_service/ ./auth_service/
COPY shared/ ./shared/
COPY database/ ./database/

# Expose port
EXPOSE 8001

# Run the service
CMD ["python", "auth_service/main.py"]
