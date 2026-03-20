from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from gemini_utils import process_unstructured_input, process_image_input, process_audio_input

app = FastAPI(
    title="Aegis: Universal Crisis Bridge",
    description="Backend API for unstructured data analysis and action extraction.",
    version="1.0.0"
)

# Add CORS Middleware for Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    # Added max_length for security to prevent enormous payload attacks
    text: str = Field(..., max_length=10000, description="The unstructured text describing a situation.")

@app.get("/")
def read_root() -> dict:
    """Return a simple health check message."""
    return {"message": "Aegis API is running"}

@app.post("/process-text")
async def handle_text(request: TextRequest) -> dict:
    """Process unstructured text to extract critical actions and details."""
    result = process_unstructured_input(request.text)
    return result

@app.post("/process-media")
async def handle_media(file: UploadFile = File(...)) -> dict:
    """
    Process uploaded image or audio files.
    Enforces a strict size limit and MIME type validation for security.
    """
    contents = await file.read()
    
    # Check strict size limit (e.g. 10MB)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    valid_image_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    valid_audio_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-m4a"]

    if file.content_type in valid_image_types:
        result = process_image_input(contents, file.content_type)
    elif file.content_type in valid_audio_types:
        result = process_audio_input(contents, file.content_type)
    else:
        raise HTTPException(
            status_code=415, 
            detail=f"Unsupported media type: {file.content_type}. Supported types: Image (jpeg, png, webp) or Audio (mp3, wav, m4a)."
        )
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
