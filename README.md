# LotusHealth - Healthcare Management System

A microservices-based healthcare management system with AI integration.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.10+

### 1. Start the System
```bash
# Start all services
docker compose -f docker-compose-postgres.yml up -d

# Check service status
docker compose -f docker-compose-postgres.yml ps
```

### 2. Initialize Database
```bash
# Run database initialization
python3 database/run_migration.py

# Load demo data
python3 database/run_demo_data.py
```

### 3. Access Services
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Auth Service**: http://localhost:8001
- **Clinic Service**: http://localhost:8002
- **AI Service**: http://localhost:8003

### 4. Default Login
- **Admin**: admin@lotushealth.com / admin123
- **Doctor**: dr.smith@lotushealth.com / doctor123
- **Patient**: john.doe@lotushealth.com / patient123

## Project Structure

```
lotushealth/
├── database/                 # Database models and scripts
│   ├── models/              # SQLAlchemy models
│   ├── connection.py        # Database connection
│   ├── init_simple.sql      # Database schema
│   ├── run_migration.py     # Database initialization
│   └── run_demo_data.py     # Demo data loader
├── services/                 # Microservices
│   ├── frontend/            # React frontend
│   ├── api_gateway/         # API Gateway service
│   ├── auth_service/        # Authentication service
│   ├── clinic_service/      # Clinic management service
│   └── ai_service/          # AI/LLM service
├── shared/                   # Shared models and utilities
├── llm_integration/          # LLM integration utilities
├── docker-compose-postgres.yml  # Docker compose configuration
└── requirements.txt          # Python dependencies
```

## Development

### Adding New Features
1. Update models in `database/models/`
2. Modify service endpoints in `services/*/routers*.py`
3. Update shared models in `shared/models.py`
4. Test with demo data

### Database Changes
1. Modify `database/init_simple.sql`
2. Update `database/run_migration.py`
3. Rebuild and restart services

## Troubleshooting

### Common Issues
- **Port conflicts**: Check if ports 3000, 8000-8003 are available
- **Database connection**: Ensure PostgreSQL container is running
- **Build errors**: Clear Docker cache with `docker system prune -a`

### Logs
```bash
# View service logs
docker compose -f docker-compose-postgres.yml logs [service_name]

# Follow logs in real-time
docker compose -f docker-compose-postgres.yml logs -f [service_name]
```

## AI Agent Testing

Use the AI Agent page in the frontend to test:
- Patient consultation
- Medical record analysis
- Treatment recommendations
- Risk assessment

See `AI_AGENT_TESTING_GUIDE.md` for detailed testing scenarios.

