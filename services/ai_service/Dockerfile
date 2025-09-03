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

# Copy service code
COPY services/ai_service/ ./ai_service/
COPY shared/ ./shared/

# Expose port
EXPOSE 8000

# Run the service
CMD ["python", "ai_service/main.py"]
