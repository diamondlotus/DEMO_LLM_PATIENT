# Development Guide

## Essential Files for Development

### 1. Database Layer
- **`database/models/`** - SQLAlchemy models for all entities
- **`database/init_simple.sql`** - Database schema and initial setup
- **`database/run_migration.py`** - Database initialization script
- **`database/run_demo_data.py`** - Demo data loader

### 2. Service Layer
- **`services/*/main.py`** - Service entry points
- **`services/*/routers*.py`** - API endpoints and business logic
- **`shared/models.py`** - Pydantic models for API requests/responses

### 3. Configuration
- **`docker-compose-postgres.yml`** - Service orchestration
- **`requirements.txt`** - Python dependencies

## Development Workflow

### 1. Database Changes
```bash
# 1. Modify database/models/*.py
# 2. Update database/init_simple.sql if schema changes
# 3. Update database/run_migration.py if needed
# 4. Rebuild and restart services
docker compose -f docker-compose-postgres.yml down
docker compose -f docker-compose-postgres.yml up -d --build
```

### 2. API Changes
```bash
# 1. Modify services/*/routers*.py
# 2. Update shared/models.py if data models change
# 3. Rebuild affected service
docker compose -f docker-compose-postgres.yml build [service_name]
docker compose -f docker-compose-postgres.yml up -d [service_name]
```

### 3. Frontend Changes
```bash
# 1. Modify services/frontend/src/
# 2. Rebuild frontend service
docker compose -f docker-compose-postgres.yml build frontend
docker compose -f docker-compose-postgres.yml up -d frontend
```

## Key Components

### Database Models
- **User**: Authentication and user management
- **Patient**: Patient information and medical records
- **Doctor**: Doctor profiles and specializations
- **Appointment**: Scheduling and patient visits
- **MedicalRecord**: Patient health history
- **KnowledgeBase**: AI knowledge storage
- **LLMInteraction**: AI conversation tracking

### API Endpoints
- **Auth Service**: Login, registration, JWT management
- **Clinic Service**: CRUD operations for patients, doctors, appointments
- **AI Service**: LLM integration and medical analysis
- **API Gateway**: Route requests to appropriate services

### Frontend Pages
- **Dashboard**: Overview and statistics
- **Patients**: Patient management
- **Doctors**: Doctor management
- **Appointments**: Scheduling and management
- **AI Agent**: LLM-powered medical consultation

## Testing with Demo Data

The system includes comprehensive demo data:
- **Users**: Admin, doctors, patients with realistic credentials
- **Patients**: Sample patient records with medical history
- **Doctors**: Various specializations and schedules
- **Appointments**: Sample appointments for testing
- **Medical Records**: Sample health data for AI analysis

## Common Development Tasks

### Adding a New Entity
1. Create model in `database/models/`
2. Add to `database/models/__init__.py`
3. Update `database/init_simple.sql`
4. Create Pydantic models in `shared/models.py`
5. Add API endpoints in appropriate service
6. Update frontend if needed

### Modifying Existing Entity
1. Update database model
2. Modify database schema if needed
3. Update API endpoints
4. Test with demo data
5. Update frontend if needed

### Adding New API Endpoint
1. Add route in `services/*/routers*.py`
2. Define request/response models in `shared/models.py`
3. Implement business logic
4. Test with appropriate data

## Debugging

### Service Logs
```bash
# View all logs
docker compose -f docker-compose-postgres.yml logs

# View specific service
docker compose -f docker-compose-postgres.yml logs [service_name]

# Follow logs in real-time
docker compose -f docker-compose-postgres.yml logs -f [service_name]
```

### Database Access
```bash
# Connect to PostgreSQL
docker compose -f docker-compose-postgres.yml exec postgres psql -U postgres -d lotushealth

# View tables
\dt

# Sample queries
SELECT * FROM users LIMIT 5;
SELECT * FROM patients LIMIT 5;
```

### Frontend Debugging
- Open browser developer tools
- Check console for errors
- Verify API calls in Network tab
- Check React component state

## Performance Tips

1. **Database**: Use indexes for frequently queried fields
2. **API**: Implement pagination for large datasets
3. **Frontend**: Use React Query for efficient data fetching
4. **Docker**: Use multi-stage builds for smaller images

## Security Considerations

1. **Authentication**: JWT tokens with proper expiration
2. **Authorization**: Role-based access control
3. **Input Validation**: Pydantic models for request validation
4. **SQL Injection**: Use SQLAlchemy ORM, avoid raw SQL
5. **Environment Variables**: Store secrets in .env files
