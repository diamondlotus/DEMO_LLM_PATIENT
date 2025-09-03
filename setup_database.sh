#!/bin/bash

# Database Setup Script for LotusHealth
# This script initializes the database and loads demo data

set -e  # Exit on any error

echo "🗄️ Setting up LotusHealth database..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not available. Please install Python 3.10+ first."
    exit 1
fi

# Check if required Python packages are available
echo "🔍 Checking Python dependencies..."
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "❌ psycopg2 is not installed. Installing required packages..."
    pip3 install psycopg2-binary sqlalchemy
fi

# Check if database is accessible
echo "🔍 Checking database connection..."
if ! python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='lotushealth',
        user='postgres',
        password='postgres'
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"; then
    echo "❌ Cannot connect to database. Please ensure:"
    echo "   1. Docker services are running"
    echo "   2. PostgreSQL container is up"
    echo "   3. Database 'lotushealth' exists"
    echo ""
    echo "Run: docker-compose -f docker-compose-postgres.yml up -d"
    exit 1
fi

# Initialize database
echo "🔧 Initializing database..."
if python3 database/run_migration.py; then
    echo "✅ Database initialized successfully"
else
    echo "❌ Database initialization failed"
    exit 1
fi

# Load demo data
echo "📊 Loading demo data..."
if python3 database/run_demo_data.py; then
    echo "✅ Demo data loaded successfully"
else
    echo "❌ Demo data loading failed"
    exit 1
fi

echo ""
echo "🎉 Database setup completed!"
echo ""
echo "📊 Database contains:"
echo "   - Users (admin, doctors, patients)"
echo "   - Sample patients with medical records"
echo "   - Sample doctors with specializations"
echo "   - Sample appointments"
echo "   - Knowledge base for AI agent"
echo ""
echo "🔑 Default login credentials:"
echo "   Admin: admin@lotushealth.com / admin123"
echo "   Doctor: dr.smith@lotushealth.com / doctor123"
echo "   Patient: john.doe@lotushealth.com / patient123"
echo ""
echo "🌐 Access the system at: http://localhost:3000"
