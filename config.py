# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")  # required
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
ADK_PORT = int(os.environ.get("ADK_PORT", "8000"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Optional enrichment adapter feature toggles
ENABLE_EXTERNAL_ENRICHMENT = os.environ.get("ENABLE_ENRICHMENT", "false").lower() == "true"
ENRICHMENT_API_KEY = os.environ.get("ENRICHMENT_API_KEY", "")
