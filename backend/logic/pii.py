"""
PII Redaction Service.
Handles removal of Personally Identifiable Information from inputs.
"""
import re
from typing import str

# Regex patterns for common Israeli/International PII
PATTERNS = {
    "israeli_id": r"\b\d{9}\b",
    "phone_il": r"\b(?:05\d-?\d{7})\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
}

def redact_text(text: str) -> str:
    """
    Scrub PII from text using regex patterns.
    Replaces sensitive data with [REDACTED].
    """
    if not text:
        return text
        
    redacted = text
    for p_name, pattern in PATTERNS.items():
        redacted = re.sub(pattern, "[REDACTED]", redacted)
        
    return redacted
