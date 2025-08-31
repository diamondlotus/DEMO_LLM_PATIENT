#!/bin/bash

set -e  # Exit on any error

echo "🔍 Debug mode: Starting LotusHealth services..."

# Check if files exist
echo "📁 Checking files..."
ls -la /app/
echo "📁 Frontend files:"
ls -la /app/frontend/
echo "📁 App files:"
ls -la /app/app/

# Check nginx config
echo "🔧 Testing nginx configuration..."
nginx -t

# Start nginx in background
echo "📡 Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!
echo "📡 Nginx started with PID: $NGINX_PID"

# Wait for nginx to start
sleep 3

# Check if nginx is running
if ps -p $NGINX_PID > /dev/null; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx failed to start"
    exit 1
fi

# Check nginx logs
echo "📋 Nginx error log:"
tail -n 5 /var/log/nginx/error.log || echo "No error log yet"

# Start FastAPI backend
echo "🐍 Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
