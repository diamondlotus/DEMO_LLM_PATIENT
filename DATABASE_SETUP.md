# 🗄️ Database Setup Guide for LotusHealth

## 🎯 **Database Architecture Overview**

### **Primary Database: PostgreSQL**
- **Purpose**: Store structured healthcare data, user management, appointments, medical records
- **Features**: ACID compliance, JSON support, full-text search, array fields, custom functions
- **Port**: 5432

### **Vector Database: ChromaDB**
- **Purpose**: Store LLM embeddings for semantic search across medical knowledge
- **Features**: Vector similarity search, medical knowledge base, patient education content
- **Port**: 8001

### **Cache Layer: Redis**
- **Purpose**: Fast access to frequently used data, session management, real-time features
- **Features**: In-memory storage, pub/sub messaging, data persistence
- **Port**: 6379

## 🚀 **Quick Start with Docker**

### **1. Start the Complete System**
```bash
# Start all services including PostgreSQL
docker-compose -f docker-compose-postgres.yml up --build

# Or start in detached mode
docker-compose -f docker-compose-postgres.yml up --build -d
```

### **2. Verify Services**
```bash
# Check service status
docker-compose -f docker-compose-postgres.yml ps

# Check logs
docker-compose -f docker-compose-postgres.yml logs postgres
docker-compose -f docker-compose-postgres.yml logs chromadb
docker-compose -f docker-compose-postgres.yml logs redis
```

## 🏗️ **Database Schema Features**

### **Core Tables**
- **users**: User authentication and role management
- **patients**: Patient demographics and medical history
- **doctors**: Doctor profiles and specializations
- **appointments**: Scheduling and appointment management
- **office_visits**: Clinical visit records
- **medical_records**: Structured medical documentation
- **schedules**: Doctor availability management

### **LLM Integration Tables**
- **llm_interactions**: Track all AI interactions
- **knowledge_base**: Medical knowledge for AI reference
- **patient_education**: AI-generated educational content

### **Advanced Features**
- **Full-text search** on medical records
- **Array fields** for medications, allergies, certifications
- **JSON fields** for flexible data storage
- **Custom functions** for patient summaries
- **Database views** for common queries
- **Triggers** for automatic timestamp updates

## 🔐 **Database Access**

### **Connection Details**
```bash
Host: localhost
Port: 5432
Database: lotushealth
Username: postgres
Password: password
```

### **Connect via psql**
```bash
psql -h localhost -U postgres -d lotushealth
```

### **Connect via Python**
```python
from database.connection import get_db, test_db_connection

# Test connection
if test_db_connection():
    print("✅ Database connected successfully")
    
# Get database session
with get_db() as db:
    # Your database operations here
    pass
```

## 🤖 **LLM Integration Features**

### **HealthcareLLM Class**
```python
from llm_integration.healthcare_llm import create_healthcare_llm

# Initialize LLM
llm = create_healthcare_llm(openai_api_key="your-key")

# Analyze patient symptoms
analysis = llm.analyze_patient_symptoms(
    symptoms="Chest pain and shortness of breath",
    patient_context="Patient has diabetes and hypertension"
)

# Generate treatment plans
plan = llm.generate_treatment_plan(
    diagnosis="Type 2 Diabetes",
    patient_context="Patient is 45 years old with no complications"
)

# Provide patient education
education = llm.provide_medical_education(
    topic="Diabetes Management",
    patient_level="basic"
)
```

### **Vector Search Capabilities**
```python
# Search medical knowledge base
results = llm.search_medical_knowledge(
    query="diabetes treatment guidelines",
    k=5
)

# Add medical knowledge
llm.add_medical_knowledge(
    documents=["Medical guideline text..."],
    metadata=[{"source": "WHO", "category": "diabetes"}]
)
```

## 📊 **Sample Data Included**

### **Users**
- **admin** / admin123 (System Administrator)
- **dr.smith** / doctor123 (Cardiologist)
- **nurse.jones** / nurse123 (Registered Nurse)
- **receptionist.wilson** / receptionist123 (Front Desk)

### **Patients**
- **John Doe**: 38-year-old male with diabetes and hypertension
- **Jane Smith**: 33-year-old female with asthma
- **Mike Johnson**: 45-year-old male with high cholesterol

### **Sample Records**
- Appointments and office visits
- Medical records with diagnoses
- Treatment plans and prescriptions

## 🔧 **Customization Options**

### **Environment Variables**
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lotushealth
DB_USER=postgres
DB_PASSWORD=password
DB_SSLMODE=prefer
DB_ECHO=false

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key-here
```

### **Database Extensions**
The system automatically enables:
- **uuid-ossp**: For UUID generation
- **pg_trgm**: For text similarity search
- **btree_gin**: For efficient array indexing

## 📈 **Performance Optimizations**

### **Indexes Created**
- Primary keys and foreign keys
- Full-text search indexes
- Array field indexes (GIN)
- Composite indexes for common queries
- Date-based indexes for time-series data

### **Connection Pooling**
- **Pool Size**: 10 connections
- **Max Overflow**: 20 additional connections
- **Connection Recycling**: Every hour
- **Pre-ping**: Connection validation

## 🧪 **Testing the Setup**

### **1. Health Checks**
```bash
# Database health
curl http://localhost:8003/health

# Individual service health
curl http://localhost:8001/health  # Auth service
curl http://localhost:8002/health  # Clinic service
curl http://localhost:8000/health  # AI service
```

### **2. Database Queries**
```sql
-- Check sample data
SELECT * FROM users;
SELECT * FROM patients;
SELECT * FROM appointments;

-- Test custom functions
SELECT get_patient_summary(patient_id) FROM patients LIMIT 1;

-- Check dashboard stats
SELECT * FROM dashboard_stats;
```

### **3. LLM Integration Test**
```python
# Test LLM connection
from llm_integration.healthcare_llm import create_healthcare_llm

llm = create_healthcare_llm()
result = llm.analyze_patient_symptoms("fever and cough")
print(result)
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose-postgres.yml logs postgres

# Verify network connectivity
docker network ls
docker network inspect lotushealth_lotushealth-network
```

#### **2. ChromaDB Issues**
```bash
# Check ChromaDB logs
docker-compose -f docker-compose-postgres.yml logs chromadb

# Verify ChromaDB is accessible
curl http://localhost:8001/api/v1/heartbeat
```

#### **3. LLM Integration Issues**
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Verify API key in environment
docker-compose -f docker-compose-postgres.yml exec ai-service env | grep OPENAI
```

### **Reset Database**
```bash
# Stop services
docker-compose -f docker-compose-postgres.yml down

# Remove volumes
docker volume rm lotushealth_postgres_data
docker volume rm lotushealth_chromadb_data

# Restart
docker-compose -f docker-compose-postgres.yml up --build
```

## 🔮 **Future Enhancements**

### **Planned Features**
- **Real-time notifications** using Redis pub/sub
- **Advanced analytics** with PostgreSQL window functions
- **Machine learning models** integration
- **HIPAA compliance** features
- **Multi-tenant support**
- **Advanced reporting** and dashboards

### **Scaling Considerations**
- **Read replicas** for high-traffic scenarios
- **Sharding** for large datasets
- **Caching strategies** for frequently accessed data
- **Backup and recovery** procedures

## 📚 **Additional Resources**

### **Documentation**
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Redis Documentation](https://redis.io/documentation)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### **Best Practices**
- **Regular backups** of PostgreSQL data
- **Monitor connection pool** usage
- **Optimize queries** using EXPLAIN ANALYZE
- **Regular maintenance** with VACUUM and ANALYZE

---

## 🎉 **Success!**

Your LotusHealth system is now running with:
- ✅ **PostgreSQL** database with healthcare schema
- ✅ **ChromaDB** vector store for LLM integration
- ✅ **Redis** cache for performance
- ✅ **Sample data** for testing
- ✅ **LLM integration** ready for patient and doctor support

**Next Steps:**
1. Test the frontend at http://localhost
2. Explore the API at http://localhost:8003/docs
3. Start building your LLM-powered healthcare features!

For support, check the logs or refer to the troubleshooting section above.
