from google import genai
from google.genai import errors, types
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, Union

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Extracted Model Name for easy configuration
MODEL_NAME = 'gemini-2.5-flash'

PROMPT_TEMPLATE = """
You are Aegis, a universal bridge between messy human intent and structured life-saving actions.
Analyze the following input and extract:
1. Criticality (Low, Medium, High, Critical)
2. Category (Medical, Environmental, Infrastructure, Human Rights, Other)
3. Location (if identifiable)
4. Summary of the situation
5. Action Items (List of structured JSON objects with 'target', 'priority', 'instruction')

Input: {input_data}

Return the response in structured JSON format obeying the exact schema requested.
"""

def _call_gemini(contents: Union[str, list]) -> Dict[str, Any]:
    """
    Helper function to call Gemini API with error handling and JSON enforcement.
    Uses Google Services 'response_mime_type' for robust output parsing.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        print(f"DEBUG: Gemini response received. Length: {len(response.text) if response.text else 0}")
        text = response.text
        # Fallback strip in case of malformed markdown wrapper despite JSON config
        if text and "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text) if text else {"error": "Empty response"}
    except errors.ClientError as e:
        if "429" in str(e):
            return {"error": "API Rate Limit Exceeded (429). Please wait a few seconds and try again.", "raw": str(e)}
        return {"error": f"Gemini API Error: {e}", "raw": str(e)}
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON response from Gemini.", "raw": str(e)}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}", "raw": str(e)}


def process_unstructured_input(data: str) -> Dict[str, Any]:
    """Process purely text-based situation descriptions."""
    prompt = PROMPT_TEMPLATE.format(input_data=data)
    print(f"DEBUG: Input data Length: {len(data)}")
    return _call_gemini(prompt)


def process_image_input(image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """Process an image situation along with a default prompt."""
    prompt = PROMPT_TEMPLATE.format(input_data="[Image Data Provided]")
    print("DEBUG: Processing image input...")
    contents = [
        prompt,
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    ]
    return _call_gemini(contents)


def process_audio_input(audio_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """Process an audio situation along with a default prompt."""
    prompt = PROMPT_TEMPLATE.format(input_data="[Audio File Provided]")
    print("DEBUG: Processing audio input...")
    contents = [
        prompt,
        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    ]
    return _call_gemini(contents)
