FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service and shared code
COPY services/ ./services/
COPY shared/ ./shared/

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "services/clinic_service/main.py"]
