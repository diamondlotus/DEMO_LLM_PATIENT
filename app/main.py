from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI(title="LotusHealth Multi-Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()   # ✅ bây giờ đã thấy WorkflowState

class PatientNoteInput(BaseModel):
    session_id: str
    note: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LotusHealth Multi-Agent API"}

@app.post("/process_note")
async def process_patient(note_input: PatientNoteInput):
    result = graph.invoke({"note": note_input.note})
    return {"report": result}

