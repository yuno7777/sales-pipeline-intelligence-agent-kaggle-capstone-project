# utils.py
import logging
import json
from typing import Any

logger = logging.getLogger("sales_agent")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def safe_str(s: Any) -> str:
    if s is None:
        return ""
    return str(s)

def require_env(varname: str, value: str):
    if not value:
        logger.error(f"Missing required env var: {varname}")
        raise RuntimeError(f"Missing required env var: {varname}")

def scrub_output_for_pii(text: str) -> str:
    # Minimal scrub: remove email-like tokens, phone-like tokens
    import re
    text = re.sub(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\+?\d[\d\-\s]{7,}\d", "[REDACTED_PHONE]", text)
    return text
