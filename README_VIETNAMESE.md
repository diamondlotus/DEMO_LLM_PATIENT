# 🏥 LotusHealth - Hướng dẫn sử dụng tiếng Việt

## 🎯 **Tổng quan hệ thống**

LotusHealth là một nền tảng chăm sóc sức khỏe AI với kiến trúc microservices, tích hợp LLM để hỗ trợ bác sĩ và bệnh nhân.

### **🏗️ Kiến trúc hệ thống**
- **Frontend**: Giao diện web hiện đại
- **API Gateway**: Điều phối tất cả requests
- **Auth Service**: Xác thực và phân quyền (RBAC)
- **Clinic Service**: Quản lý phòng khám, lịch hẹn
- **AI Service**: Tích hợp LLM cho chẩn đoán và điều trị
- **Database**: PostgreSQL + ChromaDB + Redis

## 🚀 **Cách chạy hệ thống**

### **Phương pháp 1: Sử dụng script tự động (Khuyến nghị)**

#### **Cho Linux/macOS:**
```bash
# Cấp quyền thực thi
chmod +x start.sh

# Chạy script
./start.sh
```

#### **Cho Windows:**
```cmd
# Chạy file batch
start.bat
```

#### **Cho tất cả hệ điều hành:**
```bash
# Chạy script Python
python run_all.py
```

### **Phương pháp 2: Chạy thủ công**

#### **Bước 1: Tạo file .env**
```bash
# Tạo file .env từ mẫu
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**Nội dung file .env:**
```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-here
```

#### **Bước 2: Khởi động services**
```bash
# Build và khởi động tất cả services
docker-compose -f docker-compose-postgres.yml up --build -d

# Hoặc từng bước:
docker-compose -f docker-compose-postgres.yml build
docker-compose -f docker-compose-postgres.yml up -d
```

#### **Bước 3: Kiểm tra trạng thái**
```bash
# Xem trạng thái services
docker-compose -f docker-compose-postgres.yml ps

# Xem logs
docker-compose -f docker-compose-postgres.yml logs -f
```

## 📁 **Cấu trúc thư mục mới**

```
lotushealth/
├── database/
│   ├── models/                 # 🆕 Models được tái cấu trúc
│   │   ├── __init__.py        # Import tất cả models
│   │   ├── base.py            # Base class cho SQLAlchemy
│   │   ├── user.py            # Model User
│   │   ├── patient.py         # Model Patient
│   │   ├── doctor.py          # Model Doctor
│   │   ├── appointment.py     # Model Appointment
│   │   ├── office_visit.py    # Model OfficeVisit
│   │   ├── medical_record.py  # Model MedicalRecord
│   │   ├── schedule.py        # Model Schedule
│   │   ├── llm_interaction.py # Model LLMInteraction
│   │   ├── knowledge_base.py  # Model KnowledgeBase
│   │   └── patient_education.py # Model PatientEducation
│   ├── connection.py          # Kết nối database
│   └── init.sql               # Script khởi tạo database
├── services/                   # Microservices
│   ├── auth_service/          # Service xác thực
│   ├── clinic_service/        # Service phòng khám
│   ├── api_gateway/           # API Gateway
│   ├── ai_service/            # Service AI
│   └── frontend/              # Frontend
├── llm_integration/            # Tích hợp LLM
│   └── healthcare_llm.py      # Class HealthcareLLM
├── frontend/                   # Giao diện web
├── run_all.py                  # 🆕 Script chạy tất cả
├── start.sh                    # 🆕 Script Linux/macOS
├── start.bat                   # 🆕 Script Windows
├── docker-compose-postgres.yml # Docker Compose với PostgreSQL
└── requirements.txt            # Dependencies Python
```

## 🔧 **Tái cấu trúc Models**

### **Trước đây:**
- Tất cả models trong 1 file `models.py` (khoảng 200+ dòng)
- Khó bảo trì và mở rộng
- Import/export phức tạp

### **Bây giờ:**
- Mỗi model trong file riêng biệt
- Dễ bảo trì và mở rộng
- Import/export đơn giản qua `__init__.py`

### **Cách sử dụng models mới:**
```python
# Import tất cả models
from database.models import User, Patient, Doctor, Appointment

# Hoặc import từng model
from database.models.user import User
from database.models.patient import Patient
```

## 🌐 **Truy cập hệ thống**

Sau khi khởi động thành công:

- **🏥 Frontend**: http://localhost
- **🔗 API Gateway**: http://localhost:8003
- **📚 API Documentation**: http://localhost:8003/docs
- **🗄️ PostgreSQL**: localhost:5432
- **🤖 ChromaDB**: http://localhost:8001
- **⚡ Redis**: localhost:6379

## 🔑 **Tài khoản demo**

- **👨‍💼 Admin**: admin / admin123
- **👨‍⚕️ Doctor**: dr.smith / doctor123
- **👩‍⚕️ Nurse**: nurse.jones / nurse123
- **👩‍💼 Receptionist**: receptionist.wilson / receptionist123

## 🚨 **Xử lý sự cố**

### **Lỗi thường gặp:**

#### **1. Docker không chạy**
```bash
# Kiểm tra Docker
docker --version
docker ps

# Khởi động Docker Desktop (Windows/macOS)
# Hoặc systemctl start docker (Linux)
```

#### **2. Port bị chiếm**
```bash
# Kiểm tra port đang sử dụng
lsof -i :80    # macOS/Linux
netstat -an | findstr :80  # Windows

# Dừng service đang sử dụng port
docker-compose -f docker-compose-postgres.yml down
```

#### **3. Database connection failed**
```bash
# Kiểm tra PostgreSQL
docker-compose -f docker-compose-postgres.yml logs postgres

# Restart service
docker-compose -f docker-compose-postgres.yml restart postgres
```

#### **4. LLM integration không hoạt động**
```bash
# Kiểm tra OpenAI API key
echo $OPENAI_API_KEY

# Kiểm tra logs AI service
docker-compose -f docker-compose-postgres.yml logs ai-service
```

### **Lệnh hữu ích:**

```bash
# Dừng tất cả services
docker-compose -f docker-compose-postgres.yml down

# Xóa volumes (dữ liệu)
docker-compose -f docker-compose-postgres.yml down -v

# Xem logs real-time
docker-compose -f docker-compose-postgres.yml logs -f

# Restart service cụ thể
docker-compose -f docker-compose-postgres.yml restart auth-service

# Kiểm tra resource usage
docker stats
```

## 🔄 **Cập nhật hệ thống**

### **Cập nhật code:**
```bash
# Pull code mới
git pull origin main

# Rebuild services
docker-compose -f docker-compose-postgres.yml down
docker-compose -f docker-compose-postgres.yml up --build -d
```

### **Cập nhật database schema:**
```bash
# Chạy migration (nếu có)
docker-compose -f docker-compose-postgres.yml exec postgres psql -U postgres -d lotushealth -f /path/to/migration.sql
```

## 📊 **Monitoring và Logs**

### **Kiểm tra sức khỏe hệ thống:**
```bash
# Health check API Gateway
curl http://localhost:8003/health

# Health check từng service
curl http://localhost:8001/health  # Auth service
curl http://localhost:8002/health  # Clinic service
curl http://localhost:8000/health  # AI service
```

### **Xem logs:**
```bash
# Logs của tất cả services
docker-compose -f docker-compose-postgres.yml logs

# Logs của service cụ thể
docker-compose -f docker-compose-postgres.yml logs auth-service

# Logs real-time
docker-compose -f docker-compose-postgres.yml logs -f
```

## 🎉 **Kết luận**

Với cấu trúc mới:
- ✅ **Models được tách riêng** - dễ bảo trì
- ✅ **Script tự động** - dễ khởi động
- ✅ **Docker Compose** - dễ triển khai
- ✅ **LLM Integration** - sẵn sàng cho AI
- ✅ **Database PostgreSQL** - mạnh mẽ và ổn định

**Bắt đầu ngay:**
```bash
# Chạy script tự động
python run_all.py

# Hoặc sử dụng shell script
./start.sh
```

Hệ thống sẽ tự động khởi động tất cả services và sẵn sàng sử dụng! 🚀
