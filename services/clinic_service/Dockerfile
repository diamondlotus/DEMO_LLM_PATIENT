FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/clinic_service/ ./clinic_service/

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "clinic_service/main.py"]
