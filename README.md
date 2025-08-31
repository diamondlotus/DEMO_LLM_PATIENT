# N1 Healthcare Multi-Agent Demo

This demo shows a simple **LangChain + LangGraph multi-agent pipeline** for healthcare:

- **Parser Agent** → extract structured data from patient notes  
- **Evaluator Agent** → validate against ICD/SNOMED  
- **Synthesizer Agent** → generate patient-friendly report  
- **Memory persistence** → Redis (short-term), ChromaDB (long-term)  
- **API** → FastAPI endpoint `/process_note`  

### Run
```bash
docker-compose up --build

