@echo off
chcp 65001 >nul
echo 🏥 LotusHealth - Healthcare AI Platform
echo ========================================

REM Kiểm tra Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker không được cài đặt
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose không được cài đặt
    pause
    exit /b 1
)

REM Kiểm tra file .env
if not exist .env (
    echo ⚠️  Không tìm thấy file .env
    echo    Tạo file .env với OPENAI_API_KEY
    echo    Ví dụ: OPENAI_API_KEY=your-api-key-here
    pause
    exit /b 1
)

REM Kiểm tra OPENAI_API_KEY
findstr "OPENAI_API_KEY" .env >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Không tìm thấy OPENAI_API_KEY trong file .env
    pause
    exit /b 1
)

echo ✅ Kiểm tra hoàn tất
echo.

REM Dừng services cũ nếu có
echo 🛑 Dừng services cũ...
docker-compose -f docker-compose-postgres.yml down

REM Xóa volumes cũ nếu cần
set /p choice="🗑️  Xóa dữ liệu cũ? (y/N): "
if /i "%choice%"=="y" (
    echo 🗑️  Xóa volumes...
    docker-compose -f docker-compose-postgres.yml down -v
)

REM Build services
echo 🔨 Building services...
docker-compose -f docker-compose-postgres.yml build

if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Build completed successfully
echo.

REM Khởi động services
echo 🚀 Starting services...
docker-compose -f docker-compose-postgres.yml up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo ✅ Services started successfully
echo.

REM Chờ services khởi động
echo ⏳ Chờ services khởi động...
timeout /t 10 /nobreak >nul

REM Kiểm tra trạng thái
echo 📊 Service status:
docker-compose -f docker-compose-postgres.yml ps

echo.
echo 🌐 Thông tin truy cập:
echo    🏥 Frontend: http://localhost
echo    🔗 API Gateway: http://localhost:8003
echo    📚 API Documentation: http://localhost:8003/docs
echo    🗄️  PostgreSQL: localhost:5432
echo    🤖 ChromaDB: http://localhost:8001
echo    ⚡ Redis: localhost:6379

echo.
echo 🔑 Demo Accounts:
echo    👨‍💼 Admin: admin / admin123
echo    👨‍⚕️  Doctor: dr.smith / doctor123
echo    👩‍⚕️  Nurse: nurse.jones / nurse123
echo    👩‍💼 Receptionist: receptionist.wilson / receptionist123

echo.
echo 🎯 Để dừng services: docker-compose -f docker-compose-postgres.yml down
echo 🎯 Để xem logs: docker-compose -f docker-compose-postgres.yml logs -f
echo 🎯 Để kiểm tra trạng thái: docker-compose -f docker-compose-postgres.yml ps

echo.
echo 🎉 Hệ thống đã sẵn sàng! Nhấn phím bất kỳ để thoát...
pause >nul
