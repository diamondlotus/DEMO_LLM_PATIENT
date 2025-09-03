"""
LotusHealth Clinic Service - Main Application
Clean main.py that only contains app configuration and router inclusion
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routers_postgres import router as clinic_router

# Create FastAPI app
app = FastAPI(title="LotusHealth Clinic Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clinic_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "LotusHealth Clinic Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
