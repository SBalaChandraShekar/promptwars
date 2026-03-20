import pytest
from unittest.mock import patch, MagicMock
from gemini_utils import _call_gemini, process_unstructured_input
import json

@patch("gemini_utils.client.models.generate_content")
def test_call_gemini_success(mock_generate_content):
    # Mock the response structure
    mock_response = MagicMock()
    mock_response.text = '{"Criticality": "High", "Category": "Medical"}'
    mock_generate_content.return_value = mock_response
    
    result = _call_gemini("Test prompt")
    
    assert result == {"Criticality": "High", "Category": "Medical"}
    mock_generate_content.assert_called_once()

@patch("gemini_utils.client.models.generate_content")
def test_call_gemini_json_markdown(mock_generate_content):
    # Mock the response structure wrapped in markdown
    mock_response = MagicMock()
    mock_response.text = '```json\n{"Criticality": "Low"}\n```'
    mock_generate_content.return_value = mock_response
    
    result = _call_gemini("Test prompt")
    
    assert result == {"Criticality": "Low"}
    mock_generate_content.assert_called_once()

@patch("gemini_utils.client.models.generate_content")
def test_call_gemini_invalid_json(mock_generate_content):
    mock_response = MagicMock()
    mock_response.text = 'This is not json'
    mock_generate_content.return_value = mock_response
    
    result = _call_gemini("Test prompt")
    
    assert "error" in result
    assert "Failed to parse JSON" in result["error"]
