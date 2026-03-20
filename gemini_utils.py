"""
Gemini AI utilities for the Aegis application.
Provides structured content generation using the Google Gemini SDK
with advanced features: Safety Settings, Structured Output Schemas,
System Instructions, and typed response configurations.
"""
from google import genai
from google.genai import errors, types
import json
from typing import Dict, Any, Union, Optional, List
from config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, logger

# Initialize the Gemini Client
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- Advanced Google Services: Structured Output Schema ---
# Define a strict JSON schema for the Gemini response to guarantee structure.
# This uses the Gemini SDK's native schema support rather than relying on prompt engineering.
AEGIS_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "Criticality": types.Schema(
            type=types.Type.STRING,
            enum=["Low", "Medium", "High", "Critical"],
            description="The urgency level of the situation.",
        ),
        "Category": types.Schema(
            type=types.Type.STRING,
            enum=["Medical", "Environmental", "Infrastructure", "Human Rights", "Other"],
            description="Classification category of the crisis.",
        ),
        "Location": types.Schema(
            type=types.Type.STRING,
            description="Geographic location if identifiable from the input.",
        ),
        "Summary": types.Schema(
            type=types.Type.STRING,
            description="A concise summary of the situation.",
        ),
        "Action Items": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "target": types.Schema(type=types.Type.STRING, description="Who should act."),
                    "priority": types.Schema(type=types.Type.STRING, enum=["Low", "Medium", "High", "Critical"], description="Priority of the action."),
                    "instruction": types.Schema(type=types.Type.STRING, description="What action to take."),
                },
                required=["target", "priority", "instruction"],
            ),
            description="List of structured action items.",
        ),
    },
    required=["Criticality", "Category", "Location", "Summary", "Action Items"],
)

# --- Advanced Google Services: Safety Settings ---
# Configure safety thresholds to allow crisis-related content through without being blocked.
SAFETY_SETTINGS = [
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_ONLY_HIGH",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_ONLY_HIGH",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_ONLY_HIGH",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_ONLY_HIGH",
    ),
]

# --- Advanced Google Services: System Instruction ---
SYSTEM_INSTRUCTION = """You are Aegis, a universal bridge between messy human intent and structured life-saving actions.
Your role is to analyze crisis situations and extract structured, actionable intelligence.
Always identify the criticality, category, location, summarize the situation, and provide clear action items.
Be precise, empathetic, and prioritize human safety above all else."""

PROMPT_TEMPLATE = """Analyze the following input and extract structured crisis information:

Input: {input_data}

Provide your analysis following the required response schema exactly."""


def _build_generation_config() -> types.GenerateContentConfig:
    """
    Build the generation configuration with all advanced Google Services features.
    Uses response_mime_type, response_schema, safety_settings, and system_instruction.
    """
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AEGIS_RESPONSE_SCHEMA,
        safety_settings=SAFETY_SETTINGS,
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.3,
        max_output_tokens=2048,
    )


def _call_gemini(contents: Union[str, list]) -> Dict[str, Any]:
    """
    Core function to call the Gemini API with full error handling.

    Args:
        contents: Either a text prompt string or a list of multimodal parts.

    Returns:
        A dictionary containing the structured crisis analysis or an error object.
    """
    try:
        config = _build_generation_config()
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=contents,
            config=config,
        )
        logger.info("Gemini response received. Length: %d", len(response.text) if response.text else 0)

        text = response.text
        if not text:
            logger.warning("Gemini returned an empty response.")
            return {"error": "Empty response from Gemini."}

        # Fallback strip in case of malformed markdown wrapper
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()

        return json.loads(text)

    except errors.ClientError as e:
        error_str = str(e)
        if "429" in error_str:
            logger.error("Gemini API Rate Limit hit (429).")
            return {"error": "API Rate Limit Exceeded (429). Please wait and try again.", "raw": error_str}
        logger.error("Gemini ClientError: %s", error_str)
        return {"error": f"Gemini API Error: {e}", "raw": error_str}
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON from Gemini response: %s", e)
        return {"error": "Failed to parse JSON response from Gemini.", "raw": str(e)}
    except Exception as e:
        logger.exception("Unexpected error during Gemini API call.")
        return {"error": f"Unexpected Error: {e}", "raw": str(e)}


def process_unstructured_input(data: str) -> Dict[str, Any]:
    """
    Process a text-based situation description through Gemini.

    Args:
        data: The raw unstructured text describing a crisis.

    Returns:
        Structured crisis analysis dictionary.
    """
    prompt = PROMPT_TEMPLATE.format(input_data=data)
    logger.info("Processing text input. Length: %d characters.", len(data))
    return _call_gemini(prompt)


def process_image_input(image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Process an image through Gemini for crisis analysis.

    Args:
        image_bytes: The raw bytes of the image file.
        mime_type: The MIME type of the image (e.g., image/jpeg).

    Returns:
        Structured crisis analysis dictionary.
    """
    prompt = PROMPT_TEMPLATE.format(input_data="[Image Data Provided - Analyze the visual content]")
    logger.info("Processing image input. MIME: %s, Size: %d bytes.", mime_type, len(image_bytes))
    contents = [
        prompt,
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
    ]
    return _call_gemini(contents)


def process_audio_input(audio_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Process an audio file through Gemini for crisis analysis.

    Args:
        audio_bytes: The raw bytes of the audio file.
        mime_type: The MIME type of the audio (e.g., audio/mpeg).

    Returns:
        Structured crisis analysis dictionary.
    """
    prompt = PROMPT_TEMPLATE.format(input_data="[Audio File Provided - Transcribe and analyze]")
    logger.info("Processing audio input. MIME: %s, Size: %d bytes.", mime_type, len(audio_bytes))
    contents = [
        prompt,
        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
    ]
    return _call_gemini(contents)
