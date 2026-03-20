# Aegis: Universal Crisis Bridge

A Gemini-powered platform that converts messy, real-world inputs (text, images, audio) into structured, life-saving actions.

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐
│  Streamlit   │─────▶│  FastAPI      │─────▶│  Google Gemini API   │
│  Frontend    │◀─────│  Backend      │◀─────│  (Structured Output) │
│  (app.py)    │      │  (main.py)    │      │  + Safety Settings   │
└──────────────┘      └──────┬───────┘      └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Google Cloud    │
                    │  Firestore       │
                    │  (History &      │
                    │   Audit Trail)   │
                    └──────────────────┘
```

## Google Cloud Services Used

| Service | Purpose |
|---------|---------|
| **Gemini API** | Multi-modal AI analysis with structured output schemas, safety settings, and system instructions |
| **Cloud Firestore** | Persistent storage for analysis history and audit trail |
| **Cloud Run** | Containerized deployment with auto-scaling |
| **Cloud Logging** | Structured application logging |

## Key Features

- **Multi-Modal Input**: Text, image (JPEG/PNG/WebP), and audio (MP3/WAV/M4A) analysis
- **Structured Output**: Type-safe JSON responses enforced via Gemini `response_schema`
- **Safety Controls**: Configurable `safety_settings` to handle crisis-related content
- **Response Caching**: `@st.cache_data` prevents redundant API calls
- **File Validation**: Strict MIME type checking and 10MB size limits
- **Audit Trail**: Every analysis is persisted to Google Cloud Firestore
- **Centralized Config**: All settings managed via `config.py` and environment variables

## Project Structure

```
promptwars/
├── main.py              # FastAPI backend with API endpoints  
├── gemini_utils.py      # Gemini AI integration with advanced features
├── firestore_utils.py   # Google Cloud Firestore persistence layer
├── config.py            # Centralized configuration and logging
├── app.py               # Streamlit frontend with accessibility
├── test_main.py         # API endpoint tests (pytest)
├── test_gemini.py       # Gemini integration tests (pytest)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Cloud Run container definition
├── .env                 # Environment variables (not committed)
└── README.md            # This file
```

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run frontend (in another terminal)
streamlit run app.py

# Run tests
pytest -v
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | — | Gemini API key from AI Studio |
| `GCP_PROJECT_ID` | No | — | Google Cloud project (for Firestore) |
| `GEMINI_MODEL_NAME` | No | `gemini-2.5-flash` | Model to use |
| `MAX_TEXT_LENGTH` | No | `10000` | Max input text characters |
| `MAX_FILE_SIZE_MB` | No | `10` | Max upload size in MB |
| `LOG_LEVEL` | No | `INFO` | Python logging level |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |

## Deployment

The app is containerized and ready for Google Cloud Run:

```bash
gcloud run deploy aegis --source . --region us-central1
```

## License

Built for societal benefit using Google Gemini. Hackathon project.