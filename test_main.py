import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Aegis API is running"}

@patch("main.process_unstructured_input")
def test_handle_text_valid(mock_process):
    mock_process.return_value = {"Criticality": "High", "Category": "Infrastructure"}
    response = client.post("/process-text", json={"text": "Road blocked by fallen tree."})
    
    assert response.status_code == 200
    assert response.json() == {"Criticality": "High", "Category": "Infrastructure"}
    mock_process.assert_called_once_with("Road blocked by fallen tree.")

def test_handle_text_invalid_too_long():
    long_text = "A" * 15000
    response = client.post("/process-text", json={"text": long_text})
    assert response.status_code == 422 # Pydantic validation error

@patch("main.process_image_input")
def test_handle_media_image(mock_process_image):
    mock_process_image.return_value = {"Criticality": "Medium"}
    
    # Create a dummy image file
    file_bytes = b"fake image content"
    response = client.post(
        "/process-media",
        files={"file": ("test.jpg", file_bytes, "image/jpeg")}
    )
    
    assert response.status_code == 200
    assert response.json() == {"Criticality": "Medium"}
    mock_process_image.assert_called_once_with(file_bytes, "image/jpeg")

def test_handle_media_invalid_type():
    file_bytes = b"fake pdf content"
    response = client.post(
        "/process-media",
        files={"file": ("test.pdf", file_bytes, "application/pdf")}
    )
    assert response.status_code == 415
    assert "Unsupported media type" in response.json()["detail"]

def test_handle_media_too_large():
    file_bytes = b"A" * (11 * 1024 * 1024) # 11 MB
    response = client.post(
        "/process-media",
        files={"file": ("test.jpg", file_bytes, "image/jpeg")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
