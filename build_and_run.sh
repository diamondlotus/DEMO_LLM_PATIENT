#!/bin/bash

# LotusHealth Build and Run Script
# This script builds and starts all services with proper error handling

set -e  # Exit on any error

echo "🏥 Building and starting LotusHealth system..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Use docker compose (newer version) if available, otherwise fallback to docker-compose
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use. Please free up port $port first."
        exit 1
    fi
}

# Check required ports
echo "🔍 Checking port availability..."
check_port 3000  # Frontend
check_port 8000  # API Gateway
check_port 8001  # Auth Service
check_port 8002  # Clinic Service
check_port 8003  # AI Service
check_port 5432  # PostgreSQL

echo "✅ All ports are available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
if $DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml down > /dev/null 2>&1; then
    echo "   Stopped existing containers"
else
    echo "   No existing containers to stop"
fi

# Build all services
echo "🔨 Building services..."
$DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml build --no-cache

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

# Start services
echo "🚀 Starting services..."
$DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ Services started successfully"
else
    echo "❌ Failed to start services. Please check the error messages above."
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service status:"
$DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml ps

echo ""
echo "🎉 LotusHealth is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 API Gateway: http://localhost:8000"
echo "🔐 Auth Service: http://localhost:8001"
echo "🏥 Clinic Service: http://localhost:8002"
echo "🤖 AI Service: http://localhost:8003"
echo ""
echo "📚 Next steps:"
echo "1. Initialize database: python3 database/run_migration.py"
echo "2. Load demo data: python3 database/run_demo_data.py"
echo "3. Access frontend at http://localhost:3000"
echo ""
echo "🔍 To view logs: $DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml logs -f [service_name]"
echo "🛑 To stop: $DOCKER_COMPOSE_CMD -f docker-compose-postgres.yml down"
