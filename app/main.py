from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI()
graph = build_graph()   # ✅ bây giờ đã thấy WorkflowState

class PatientNoteInput(BaseModel):
    session_id: str
    note: str

@app.post("/process_note")
async def process_patient(note_input: PatientNoteInput):
    result = graph.invoke({"note": note_input.note})
    return {"report": result}

