#!/bin/bash

echo "🔧 Quick Fix for LotusHealth Docker Issues"
echo "=========================================="

# Stop any running containers
echo "🛑 Stopping containers..."
docker-compose down

# Remove old images
echo "🗑️  Removing old images..."
docker-compose rm -f

# Build without cache
echo "🔨 Building without cache..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check container status
echo "📊 Container status:"
docker-compose ps

# Check logs
echo "📋 Recent logs:"
docker-compose logs --tail=20 api

# Test endpoints
echo "🧪 Testing endpoints..."
echo "Testing API health..."
curl -s http://localhost:8000/health || echo "❌ API not responding"

echo "Testing frontend..."
curl -s http://localhost/ | head -n 5 || echo "❌ Frontend not responding"

echo ""
echo "🎯 If tests fail, check the logs above for errors."
echo "💡 Try accessing:"
echo "   Frontend: http://localhost"
echo "   API: http://localhost:8000"
