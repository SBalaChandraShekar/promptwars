"""Tests for the Gemini AI integration utilities."""
import pytest
from unittest.mock import patch, MagicMock
from gemini_utils import _call_gemini, process_unstructured_input, _build_generation_config


class TestBuildGenerationConfig:
    """Tests for the generation configuration builder."""

    def test_config_has_json_mime_type(self):
        """Generation config should enforce JSON output."""
        config = _build_generation_config()
        assert config.response_mime_type == "application/json"

    def test_config_has_response_schema(self):
        """Generation config should include a structured response schema."""
        config = _build_generation_config()
        assert config.response_schema is not None

    def test_config_has_safety_settings(self):
        """Generation config should include safety settings."""
        config = _build_generation_config()
        assert config.safety_settings is not None
        assert len(config.safety_settings) > 0

    def test_config_has_system_instruction(self):
        """Generation config should include a system instruction."""
        config = _build_generation_config()
        assert config.system_instruction is not None
        assert "Aegis" in config.system_instruction

    def test_config_temperature_is_low(self):
        """Temperature should be low for consistent crisis analysis."""
        config = _build_generation_config()
        assert config.temperature <= 0.5


class TestCallGemini:
    """Tests for the core _call_gemini function."""

    @patch("gemini_utils.client.models.generate_content")
    def test_successful_json_response(self, mock_generate):
        """Valid JSON response should be parsed correctly."""
        mock_response = MagicMock()
        mock_response.text = '{"Criticality": "High", "Category": "Medical"}'
        mock_generate.return_value = mock_response

        result = _call_gemini("Test prompt")

        assert result == {"Criticality": "High", "Category": "Medical"}
        mock_generate.assert_called_once()

    @patch("gemini_utils.client.models.generate_content")
    def test_markdown_wrapped_json(self, mock_generate):
        """JSON wrapped in markdown code blocks should be parsed correctly."""
        mock_response = MagicMock()
        mock_response.text = '```json\n{"Criticality": "Low"}\n```'
        mock_generate.return_value = mock_response

        result = _call_gemini("Test prompt")

        assert result == {"Criticality": "Low"}

    @patch("gemini_utils.client.models.generate_content")
    def test_invalid_json_returns_error(self, mock_generate):
        """Non-JSON response should return a descriptive error."""
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_generate.return_value = mock_response

        result = _call_gemini("Test prompt")

        assert "error" in result
        assert "Failed to parse JSON" in result["error"]

    @patch("gemini_utils.client.models.generate_content")
    def test_empty_response_returns_error(self, mock_generate):
        """Empty response from Gemini should return an error."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_generate.return_value = mock_response

        result = _call_gemini("Test prompt")

        assert "error" in result


class TestProcessUnstructuredInput:
    """Tests for the text processing function."""

    @patch("gemini_utils._call_gemini")
    def test_formats_prompt_correctly(self, mock_call):
        """Input data should be inserted into the prompt template."""
        mock_call.return_value = {"Criticality": "Low"}

        result = process_unstructured_input("Flooding in sector 4")

        assert result == {"Criticality": "Low"}
        call_args = mock_call.call_args[0][0]
        assert "Flooding in sector 4" in call_args
