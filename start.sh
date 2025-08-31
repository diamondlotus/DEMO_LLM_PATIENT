#!/bin/bash

echo "🏥 LotusHealth - Healthcare AI Platform"
echo "========================================"

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker không được cài đặt"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose không được cài đặt"
    exit 1
fi

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "⚠️  Không tìm thấy file .env"
    echo "   Tạo file .env với OPENAI_API_KEY"
    echo "   Ví dụ: OPENAI_API_KEY=your-api-key-here"
    exit 1
fi

# Kiểm tra OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY" .env; then
    echo "❌ Không tìm thấy OPENAI_API_KEY trong file .env"
    exit 1
fi

echo "✅ Kiểm tra hoàn tất"
echo ""

# Dừng services cũ nếu có
echo "🛑 Dừng services cũ..."
docker-compose -f docker-compose-postgres.yml down

# Xóa volumes cũ nếu cần
read -p "🗑️  Xóa dữ liệu cũ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Xóa volumes..."
    docker-compose -f docker-compose-postgres.yml down -v
fi

# Build services
echo "🔨 Building services..."
docker-compose -f docker-compose-postgres.yml build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build completed successfully"
echo ""

# Khởi động services
echo "🚀 Starting services..."
docker-compose -f docker-compose-postgres.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi

echo "✅ Services started successfully"
echo ""

# Chờ services khởi động
echo "⏳ Chờ services khởi động..."
sleep 10

# Kiểm tra trạng thái
echo "📊 Service status:"
docker-compose -f docker-compose-postgres.yml ps

echo ""
echo "🌐 Thông tin truy cập:"
echo "   🏥 Frontend: http://localhost"
echo "   🔗 API Gateway: http://localhost:8003"
echo "   📚 API Documentation: http://localhost:8003/docs"
echo "   🗄️  PostgreSQL: localhost:5432"
echo "   🤖 ChromaDB: http://localhost:8001"
echo "   ⚡ Redis: localhost:6379"

echo ""
echo "🔑 Demo Accounts:"
echo "   👨‍💼 Admin: admin / admin123"
echo "   👨‍⚕️  Doctor: dr.smith / doctor123"
echo "   👩‍⚕️  Nurse: nurse.jones / nurse123"
echo "   👩‍💼 Receptionist: receptionist.wilson / receptionist123"

echo ""
echo "🎯 Để dừng services: docker-compose -f docker-compose-postgres.yml down"
echo "🎯 Để xem logs: docker-compose -f docker-compose-postgres.yml logs -f"
echo "🎯 Để kiểm tra trạng thái: docker-compose -f docker-compose-postgres.yml ps"
