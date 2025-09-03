FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copy service code
COPY services/ai_service/ ./ai_service/
=======
# Copy service and shared code so package imports resolve
COPY services/ ./services/
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

<<<<<<< HEAD
# Run the service
CMD ["python", "ai_service/main.py"]
=======
# Run the service (package path)
CMD ["uvicorn", "services.ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a
