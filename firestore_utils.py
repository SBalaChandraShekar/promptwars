"""
Google Cloud Firestore integration for Aegis.
Stores analysis history for auditing and dashboard analytics.
Uses google-cloud-firestore for deep Google Cloud ecosystem integration.
"""
import os
import datetime
from typing import Dict, Any, Optional
from config import logger, GCP_PROJECT_ID

# Firestore client (lazy-loaded)
_firestore_client = None
COLLECTION_NAME = "aegis_analysis_history"


def _get_firestore_client():
    """Lazy-initialize the Firestore client. Returns None if unavailable."""
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    try:
        from google.cloud import firestore
        if GCP_PROJECT_ID:
            _firestore_client = firestore.Client(project=GCP_PROJECT_ID)
        else:
            _firestore_client = firestore.Client()
        logger.info("Firestore client initialized successfully.")
        return _firestore_client
    except Exception as e:
        logger.warning("Firestore unavailable (running locally?): %s", e)
        return None


def save_analysis_result(
    input_type: str,
    input_summary: str,
    result: Dict[str, Any],
) -> Optional[str]:
    """
    Save an analysis result to Firestore for auditing and history.

    Args:
        input_type: The type of input ('text', 'image', 'audio').
        input_summary: A short summary of the input (e.g., first 200 chars).
        result: The structured analysis result from Gemini.

    Returns:
        The Firestore document ID if saved, or None if Firestore is unavailable.
    """
    db = _get_firestore_client()
    if db is None:
        logger.debug("Skipping Firestore save — client not available.")
        return None

    try:
        doc_data = {
            "input_type": input_type,
            "input_summary": input_summary[:500],
            "result": result,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "criticality": result.get("Criticality", "Unknown"),
            "category": result.get("Category", "Unknown"),
        }
        _, doc_ref = db.collection(COLLECTION_NAME).add(doc_data)
        logger.info("Analysis saved to Firestore: %s", doc_ref.id)
        return doc_ref.id
    except Exception as e:
        logger.error("Failed to save to Firestore: %s", e)
        return None


def get_recent_analyses(limit: int = 10):
    """
    Retrieve recent analysis results from Firestore.

    Args:
        limit: Maximum number of results to return.

    Returns:
        A list of recent analysis dictionaries, or an empty list if unavailable.
    """
    db = _get_firestore_client()
    if db is None:
        return []

    try:
        docs = (
            db.collection(COLLECTION_NAME)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error("Failed to fetch from Firestore: %s", e)
        return []
