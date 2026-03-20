from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import uvicorn
from gemini_utils import process_unstructured_input, process_image_input, process_audio_input

app = FastAPI(title="Aegis: Universal Crisis Bridge")

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Aegis API is running"}

@app.post("/process-text")
async def handle_text(request: TextRequest):
    result = process_unstructured_input(request.text)
    return result

@app.post("/process-media")
async def handle_media(file: UploadFile = File(...)):
    contents = await file.read()
    if file.content_type.startswith("image/"):
        result = process_image_input(contents, file.content_type)
    elif file.content_type.startswith("audio/"):
        result = process_audio_input(contents, file.content_type)
    else:
        # Generic fallback
        result = process_image_input(contents, file.content_type) # Part.from_bytes is generic
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
