FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service and shared code so package imports resolve
COPY services/ ./services/
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

# Run the service (package path)
CMD ["uvicorn", "services.ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
