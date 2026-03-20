"""
Configuration module for the Aegis application.
Centralizes all configuration values, environment variables, and constants.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("aegis")

# --- Google Cloud / Gemini Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

# --- Application Configuration ---
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

VALID_IMAGE_TYPES = frozenset(["image/jpeg", "image/png", "image/jpg", "image/webp"])
VALID_AUDIO_TYPES = frozenset(["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-m4a"])

# --- API Configuration ---
API_TITLE = "Aegis: Universal Crisis Bridge"
API_DESCRIPTION = "A Gemini-powered backend API that converts unstructured crisis data into structured, life-saving actions."
API_VERSION = "1.0.0"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
