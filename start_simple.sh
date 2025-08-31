#!/bin/bash

echo "🚀 Starting LotusHealth services..."

# Start nginx
echo "📡 Starting nginx..."
nginx -g "daemon off;" &

# Wait a moment for nginx to start
sleep 2

# Start FastAPI backend
echo "🐍 Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
