FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements and install Python dependencies
COPY services/clinic_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copy service code, shared models, and database
COPY services/clinic_service/ ./clinic_service/
COPY shared/ ./shared/
COPY database/ ./database/
=======
# Copy service and shared code
COPY services/ ./services/
COPY shared/ ./shared/
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "services/clinic_service/main.py"]
