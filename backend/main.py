from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

app = FastAPI(title="PDF/Image Data Entry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
db: Dict[str, Dict[str, Any]] = {
    "task-123": {
        "task_id": "task-123",
        "file_name": "invoice_001.pdf",
        "extraction_status": "completed",
        "confidence_score": 0.95,
        "structured_data": {"total": 150.00, "currency": "USD"},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
}

class TaskUpdate(BaseModel):
    structured_data: Dict[str, Any]

@app.post("/api/v1/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_file(file_name: str):
    task_id = str(uuid.uuid4())
    db[task_id] = {
        "task_id": task_id,
        "file_name": file_name,
        "extraction_status": "processing",
        "confidence_score": 0.0,
        "structured_data": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    return {"task_id": task_id, "status": "processing"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in db:
        raise HTTPException(status_code=404, detail="Task not found")
    return db[task_id]

@app.patch("/api/v1/tasks/{task_id}/validate")
async def validate_task(task_id: str, update: TaskUpdate):
    if task_id not in db:
        raise HTTPException(status_code=404, detail="Task not found")
    db[task_id]["structured_data"] = update.structured_data
    db[task_id]["extraction_status"] = "validated"
    db[task_id]["updated_at"] = datetime.utcnow().isoformat()
    return db[task_id]

@app.get("/api/v1/analytics/throughput")
async def get_analytics():
    return {"total_processed": len(db), "avg_confidence": 0.95}
