"""
Aegis FastAPI Backend Application.
Provides API endpoints for processing unstructured crisis data via Google Gemini.
"""
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from config import (
    API_TITLE, API_DESCRIPTION, API_VERSION,
    CORS_ORIGINS, MAX_TEXT_LENGTH, MAX_FILE_SIZE_BYTES,
    VALID_IMAGE_TYPES, VALID_AUDIO_TYPES, logger,
)
from gemini_utils import process_unstructured_input, process_image_input, process_audio_input
from firestore_utils import save_analysis_result, get_recent_analyses

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# --- Security: CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextRequest(BaseModel):
    """Request model for text-based crisis analysis."""

    text: str = Field(
        ...,
        max_length=MAX_TEXT_LENGTH,
        description="The unstructured text describing a crisis situation.",
        json_schema_extra={"example": "Flooding in sector 4, need immediate rescue."},
    )


@app.get("/", tags=["Health"])
def read_root() -> dict:
    """Health check endpoint to verify the API is operational."""
    return {"status": "healthy", "service": API_TITLE, "version": API_VERSION}


@app.post("/process-text", tags=["Analysis"])
async def handle_text(request: TextRequest) -> dict:
    """
    Analyze unstructured text input to extract structured crisis actions.

    Uses Google Gemini with structured output schemas and safety settings.
    """
    logger.info("Received text analysis request. Length: %d", len(request.text))
    result = process_unstructured_input(request.text)
    # Google Cloud Firestore: persist for auditing
    save_analysis_result("text", request.text[:200], result)
    return result


@app.post("/process-media", tags=["Analysis"])
async def handle_media(file: UploadFile = File(...)) -> dict:
    """
    Analyze uploaded image or audio files for crisis intelligence.

    Enforces strict size limits and MIME type validation.
    Supports: JPEG, PNG, WebP images and MP3, WAV, M4A audio.
    """
    contents = await file.read()

    # Security: File size validation
    if len(contents) > MAX_FILE_SIZE_BYTES:
        logger.warning("Rejected file upload: %s (%d bytes exceeds limit).", file.filename, len(contents))
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # Security: MIME type validation
    if file.content_type in VALID_IMAGE_TYPES:
        logger.info("Processing image file: %s (%s)", file.filename, file.content_type)
        result = process_image_input(contents, file.content_type)
        save_analysis_result("image", f"Image: {file.filename}", result)
    elif file.content_type in VALID_AUDIO_TYPES:
        logger.info("Processing audio file: %s (%s)", file.filename, file.content_type)
        result = process_audio_input(contents, file.content_type)
        save_analysis_result("audio", f"Audio: {file.filename}", result)
    else:
        logger.warning("Rejected unsupported media type: %s", file.content_type)
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported media type: {file.content_type}. "
                "Supported: Image (jpeg, png, webp), Audio (mp3, wav, m4a)."
            ),
        )
    return result


@app.get("/history", tags=["History"])
def get_history(limit: int = 10) -> list:
    """
    Retrieve recent analysis history from Google Cloud Firestore.
    Returns an empty list if Firestore is not configured.
    """
    return get_recent_analyses(limit=limit)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
