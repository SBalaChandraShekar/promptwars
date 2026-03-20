from google import genai
from google.genai import errors
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

PROMPT_TEMPLATE = """
You are Aegis, a universal bridge between messy human intent and structured life-saving actions.
Analyze the following input and extract:
1. Criticality (Low, Medium, High, Critical)
2. Category (Medical, Environmental, Infrastructure, Human Rights, Other)
3. Location (if identifiable)
4. Summary of the situation
5. Action Items (List of structured JSON objects with 'target', 'priority', 'instruction')

Input: {input_data}

Return the response in structured JSON format.
"""

def process_unstructured_input(data: str):
    prompt = PROMPT_TEMPLATE.format(input_data=data)
    print(f"DEBUG: Input data Length: {len(data)}")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        print(f"DEBUG: Gemini response received. Length: {len(response.text) if response.text else 0}")
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except errors.ClientError as e:
        if "429" in str(e):
            return {"error": "API Rate Limit Exceeded (429). Please wait a few seconds and try again.", "raw": str(e)}
        return {"error": f"Gemini API Error: {e}", "raw": str(e)}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}", "raw": str(e)}

def process_image_input(image_bytes: bytes, mime_type: str):
    from google.genai import types
    prompt = PROMPT_TEMPLATE.format(input_data="[Image Data Provided]")
    print(f"DEBUG: Processing image input...")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            ]
        )
        print(f"DEBUG: Gemini response received.")
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except errors.ClientError as e:
        if "429" in str(e):
            return {"error": "API Rate Limit Exceeded (429). Please wait a few seconds and try again.", "raw": str(e)}
        return {"error": f"Gemini API Error: {e}", "raw": str(e)}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}", "raw": str(e)}

def process_audio_input(audio_bytes: bytes, mime_type: str):
    from google.genai import types
    prompt = PROMPT_TEMPLATE.format(input_data="[Audio File Provided]")
    print(f"DEBUG: Processing audio input...")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
            ]
        )
        print(f"DEBUG: Gemini response received.")
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except errors.ClientError as e:
        if "429" in str(e):
            return {"error": "API Rate Limit Exceeded (429). Please wait a few seconds and try again.", "raw": str(e)}
        return {"error": f"Gemini API Error: {e}", "raw": str(e)}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}", "raw": str(e)}
