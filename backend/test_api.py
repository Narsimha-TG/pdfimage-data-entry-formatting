import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_analytics():
    response = client.get("/api/v1/analytics/throughput")
    assert response.status_code == 200
    data = response.json()
    assert "total_processed" in data
    assert "avg_confidence" in data

def test_ingest_file_success():
    payload = {"file_name": "test_document.pdf"}
    response = client.post("/api/v1/ingest", params=payload)
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"

def test_get_task_not_found():
    response = client.get("/api/v1/tasks/non-existent-id")
    assert response.status_code == 404

def test_validate_task_flow():
    # First ingest
    ingest_res = client.post("/api/v1/ingest", params={"file_name": "invoice.png"})
    task_id = ingest_res.json()["task_id"]
    
    # Then validate
    update_data = {"structured_data": {"total": 200.0, "currency": "EUR"}}
    response = client.patch(f"/api/v1/tasks/{task_id}/validate", json=update_data)
    
    assert response.status_code == 200
    assert response.json()["extraction_status"] == "validated"
    assert response.json()["structured_data"]["total"] == 200.0