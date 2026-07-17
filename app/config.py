"""Settings, read from the environment (and a local .env file)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Override with GEMINI_MODEL to use a different model.
MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Replies are short, so this is plenty of room.
MAX_TOKENS: int = 2048

# Low temperature keeps answers consistent and close to the evidence.
TEMPERATURE: float = 0.0

# Model used to turn text into vectors for similarity search.
EMBED_MODEL: str = "gemini-embedding-001"

# How many research chunks a search returns.
TOP_K: int = 4

# Safety limit on tool-calling rounds within a single reply.
MAX_ITERS: int = 5

# Similarity cutoffs that sort a chunk into high / medium / low relevance.
BAND_HIGH: float = 0.75
BAND_MEDIUM: float = 0.63

# Mock data lives alongside the code, one level up from this package.
DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
CORPUS_DIR: Path = DATA_DIR / "corpus"
PRODUCTS_PATH: Path = DATA_DIR / "products.json"
CUSTOMER_PATH: Path = DATA_DIR / "customer.json"


def get_api_key() -> str:
    """Return the Gemini API key, or raise if it's missing."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY (or GOOGLE_API_KEY).")
    return key
