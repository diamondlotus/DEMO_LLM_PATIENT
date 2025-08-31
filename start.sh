#!/bin/bash

# Start nginx in the background
echo "🚀 Starting nginx..."
nginx

# Start FastAPI backend in the background
echo "🚀 Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for both services to start
sleep 3

echo "✅ Services started successfully!"
echo "🌐 Frontend: http://localhost:80 (or http://localhost)"
echo "🔗 API: http://localhost:8000"
echo "📚 API Docs: http://localhost/docs"

# Keep the container running
echo "🔄 Container is running. Press Ctrl+C to stop."
tail -f /dev/null
