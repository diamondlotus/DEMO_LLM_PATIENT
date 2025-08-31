#!/bin/bash

echo "🔍 Checking Port Usage on Your System"
echo "===================================="

# Check common ports
ports=(80 8000 3000 8080 443 22 3306 6379 8001)

echo "📊 Checking common ports:"
echo ""

for port in "${ports[@]}"; do
    echo -n "Port $port: "
    
    # Check if port is in use
    if lsof -i :$port >/dev/null 2>&1; then
        echo "🔴 IN USE"
        echo "   Process details:"
        lsof -i :$port | tail -n +2 | while read line; do
            echo "   $line"
        done
        echo ""
    else
        echo "🟢 AVAILABLE"
    fi
done

echo "🔍 Detailed Port 80 Check:"
echo "=========================="

# Detailed check for port 80
if lsof -i :80 >/dev/null 2>&1; then
    echo "❌ Port 80 is currently in use by:"
    lsof -i :80
    echo ""
    echo "💡 You may need to:"
    echo "   1. Stop the service using port 80"
    echo "   2. Change your Docker frontend port to something else (e.g., 8080)"
    echo "   3. Use port forwarding in docker-compose.yml"
else
    echo "✅ Port 80 is available for use"
fi

echo ""
echo "🔍 All Listening Ports:"
echo "======================="
lsof -i -P | grep LISTEN | head -20

echo ""
echo "💡 To free up port 80, you can:"
echo "   - Stop web servers (Apache, nginx, etc.)"
echo "   - Stop Docker containers using port 80"
echo "   - Change your application to use a different port"
