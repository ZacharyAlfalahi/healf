"""Settings, read from the environment (and a local .env file)."""

import os

from dotenv import load_dotenv

load_dotenv()

# Override with GEMINI_MODEL to use a different model.
MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Replies are short, so this is plenty of room.
MAX_TOKENS: int = 2048


def get_api_key() -> str:
    """Return the Gemini API key, or raise if it's missing."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set."
        )
    return key
