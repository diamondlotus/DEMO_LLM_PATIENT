#!/bin/bash
set -e

echo "🚀 Starting  LotusHealth Multi-Agent Demo..."

if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ No API Key found. Please insert your key inside script.sh"
  exit 1
fi

# Export for docker-compose usageỉ
export OPENAI_API_KEY

# 2. Build & Run containers
echo "🔧 Building Docker containers..."
docker compose up --build -d

echo "⏳ Waiting for API to start..."
sleep 8

# 3. Test API endpoint
echo "🧪 Sending test request..."
curl -s -X POST http://localhost:8000/process_note \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test123","note":"Patient has hypertension, taking metformin, HbA1c 7.2%"}' \
  | jq

echo "✅ Demo completed! Visit http://localhost:8000/docs to explore FastAPI Swagger UI."

