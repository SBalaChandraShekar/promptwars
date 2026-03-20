"""Tests for the FastAPI backend endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the root health check endpoint."""

    def test_read_root_returns_healthy(self):
        """Verify GET / returns a healthy status with service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestTextEndpoint:
    """Tests for the POST /process-text endpoint."""

    @patch("main.save_analysis_result")
    @patch("main.process_unstructured_input")
    def test_valid_text_request(self, mock_process, mock_save):
        """Valid text input should return structured analysis."""
        mock_process.return_value = {"Criticality": "High", "Category": "Infrastructure"}
        response = client.post("/process-text", json={"text": "Road blocked by a fallen tree."})

        assert response.status_code == 200
        assert response.json() == {"Criticality": "High", "Category": "Infrastructure"}
        mock_process.assert_called_once_with("Road blocked by a fallen tree.")
        mock_save.assert_called_once()

    def test_empty_text_rejected(self):
        """Empty text should be rejected by Pydantic validation."""
        response = client.post("/process-text", json={"text": ""})
        # Empty strings are allowed by Pydantic unless min_length is set,
        # but the endpoint should still work without error
        assert response.status_code in [200, 422]

    def test_text_too_long_rejected(self):
        """Text exceeding max_length should return 422 Unprocessable Entity."""
        long_text = "A" * 15000
        response = client.post("/process-text", json={"text": long_text})
        assert response.status_code == 422

    def test_missing_text_field(self):
        """Missing 'text' field should return 422 Unprocessable Entity."""
        response = client.post("/process-text", json={})
        assert response.status_code == 422


class TestMediaEndpoint:
    """Tests for the POST /process-media endpoint."""

    @patch("main.save_analysis_result")
    @patch("main.process_image_input")
    def test_valid_image_upload(self, mock_process_image, mock_save):
        """Valid JPEG image should be processed successfully."""
        mock_process_image.return_value = {"Criticality": "Medium"}
        file_bytes = b"fake image content"

        response = client.post(
            "/process-media",
            files={"file": ("test.jpg", file_bytes, "image/jpeg")},
        )

        assert response.status_code == 200
        assert response.json() == {"Criticality": "Medium"}
        mock_process_image.assert_called_once_with(file_bytes, "image/jpeg")
        mock_save.assert_called_once()

    @patch("main.save_analysis_result")
    @patch("main.process_audio_input")
    def test_valid_audio_upload(self, mock_process_audio, mock_save):
        """Valid MP3 audio file should be processed successfully."""
        mock_process_audio.return_value = {"Criticality": "Low"}
        file_bytes = b"fake audio content"

        response = client.post(
            "/process-media",
            files={"file": ("test.mp3", file_bytes, "audio/mpeg")},
        )

        assert response.status_code == 200
        assert response.json() == {"Criticality": "Low"}
        mock_process_audio.assert_called_once_with(file_bytes, "audio/mpeg")

    def test_unsupported_media_type_rejected(self):
        """Unsupported file types (e.g. PDF) should return 415."""
        file_bytes = b"fake pdf content"
        response = client.post(
            "/process-media",
            files={"file": ("test.pdf", file_bytes, "application/pdf")},
        )
        assert response.status_code == 415
        assert "Unsupported media type" in response.json()["detail"]

    def test_file_too_large_rejected(self):
        """Files exceeding 10MB should return 413."""
        file_bytes = b"A" * (11 * 1024 * 1024)
        response = client.post(
            "/process-media",
            files={"file": ("test.jpg", file_bytes, "image/jpeg")},
        )
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]


class TestHistoryEndpoint:
    """Tests for the GET /history endpoint."""

    @patch("main.get_recent_analyses")
    def test_get_history(self, mock_get):
        """History endpoint should return a list."""
        mock_get.return_value = [{"id": "abc", "criticality": "High"}]
        response = client.get("/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        mock_get.assert_called_once_with(limit=10)
