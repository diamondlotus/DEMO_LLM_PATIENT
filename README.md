# LotusHealth Multi-Agent Demo

This demo shows a simple **LangChain + LangGraph multi-agent pipeline** for healthcare:

- **Parser Agent** → extract structured data from patient notes  
- **Evaluator Agent** → validate against ICD/SNOMED  
- **Synthesizer Agent** → generate patient-friendly report  
- **Memory persistence** → Redis (short-term), ChromaDB (long-term)  
- **API** → FastAPI endpoint `/process_note`  

## 🏗️ Architecture Overview 

The system implements a multi-agent workflow using LangGraph:

```
Patient Note → Parser Agent → Evaluator Agent → Synthesizer Agent → Final Report
     ↓              ↓              ↓              ↓              ↓
  Input        Structured    Validated      Patient-      Output
  Text         Data         Medical        Friendly
                Extraction   Codes         Summary
```

### Components

- **Parser Agent**: Extracts structured medical data from unstructured patient notes
- **Evaluator Agent**: Validates extracted data against medical coding standards (ICD/SNOMED)
- **Synthesizer Agent**: Generates patient-friendly medical reports
- **Memory System**: 
  - Redis: Short-term session memory
  - ChromaDB: Long-term knowledge persistence
- **API Layer**: FastAPI REST endpoint for processing notes

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.8+ (for local development)
- Modern web browser

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lotushealth
   ```

2. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run with Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Redis: localhost:6379
   - ChromaDB: localhost:8001

5. **Access the Frontend**
   - Frontend: http://localhost (port 80)
   - The frontend is automatically served by nginx in the Docker container

## 📖 Usage Guide

### Frontend Interface

The project includes a modern web interface for easy testing:

- **Interactive Form**: Input patient notes and session IDs
- **Example Notes**: Pre-loaded medical scenarios for testing
- **Real-time Results**: View agent outputs in organized cards
- **Responsive Design**: Works on desktop and mobile devices

**Frontend Access:**
The frontend is automatically served by nginx when you run `docker-compose up --build`. Simply open http://localhost in your browser.

### API Endpoint

**POST** `/process_note`

Process a patient note through the multi-agent pipeline.

#### Request Body
```json
{
  "session_id": "unique_session_identifier",
  "note": "Patient presents with chest pain and shortness of breath..."
}
```

#### Response
```json
{
  "report": {
    "structured_data": {...},
    "validated_codes": {...},
    "patient_summary": "..."
  }
}
```

### Example Usage

#### Using curl
```bash
curl -X POST "http://localhost:8000/process_note" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_123",
    "note": "Patient reports chest pain radiating to left arm, duration 2 hours. Associated with diaphoresis and shortness of breath."
  }'
```

#### Using Python
```python
import requests

url = "http://localhost:8000/process_note"
data = {
    "session_id": "session_123",
    "note": "Patient reports chest pain radiating to left arm..."
}

response = requests.post(url, json=data)
result = response.json()
print(result["report"])
```

## 🛠️ Development Setup

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start services**
   ```bash
   # Start Redis
   docker run -d -p 6379:6379 redis:6.2
   
   # Start ChromaDB
   docker run -d -p 8001:8001 chromadb/chroma
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Project Structure

```
lotushealth/
├── app/
│   ├── agents.py      # Agent definitions and logic
│   ├── graph.py       # LangGraph workflow configuration
│   ├── main.py        # FastAPI application entry point
│   ├── memory.py      # Memory management (Redis/ChromaDB)
│   └── state.py       # Workflow state definitions
├── frontend/
│   └── index.html     # Modern web interface for testing
├── docker-compose.yml # Docker services configuration
├── Dockerfile         # Application container definition
├── serve_frontend.py  # Frontend server script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | Yes | - |
| `REDIS_URL` | Redis connection URL | No | `redis://localhost:6379` |
| `CHROMA_HOST` | ChromaDB host | No | `localhost` |
| `CHROMA_PORT` | ChromaDB port | No | `8001` |

### Agent Configuration

Agents can be configured in `app/agents.py`:

- **Model selection**: Choose different OpenAI models
- **Temperature**: Control response creativity
- **Memory settings**: Adjust memory retention policies
- **Validation rules**: Customize medical coding validation

## 🧪 Testing

### Automated Testing

Run the test script to verify everything is working:

```bash
# Test both frontend and API
python test_frontend.py
```

### API Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Patient Note Processing**
   ```bash
   # Use the example in the Usage Guide section
   ```

### Integration Testing

```bash
# Run tests (if test files exist)
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 📊 Monitoring & Logging

### Health Checks

- **API Health**: `GET /health`
- **Service Status**: Check individual service endpoints
- **Memory Usage**: Monitor Redis and ChromaDB metrics

### Logging

The application logs:
- Agent execution steps
- API requests/responses
- Memory operations
- Error conditions

## 🚨 Troubleshooting

### Docker Build Issues

If you encounter connection refused or nginx errors:

1. **Rebuild without cache:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

2. **Check container logs:**
   ```bash
   docker-compose logs api
   ```

3. **Use debug mode:**
   ```bash
   # Edit Dockerfile to use debug script
   CMD ["./start_debug.sh"]
   ```

4. **Verify file permissions:**
   ```bash
   docker-compose exec api ls -la /app/
   ```

### Common Issues

1. **OpenAI API Key Error**
   - Verify `OPENAI_API_KEY` is set in `.env`
   - Check API key validity and quota

2. **Service Connection Issues**
   - Ensure Redis and ChromaDB are running
   - Check port configurations in `docker-compose.yml`

3. **Memory Errors**
   - Verify Redis persistence
   - Check ChromaDB storage permissions

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
docker-compose up
```

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards

- Follow PEP 8 Python style guidelines
- Add type hints where possible
- Include docstrings for functions
- Write meaningful commit messages

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Create a GitHub issue
- Check the troubleshooting section
- Review the API documentation at `/docs`

---

**Note**: This is a demo application. For production use, ensure proper security measures, error handling, and compliance with healthcare regulations.

