"""Similarity search over the research corpus, using Gemini embeddings."""

import json
from pathlib import Path

import numpy as np
from google import genai
from google.genai import types

from app import config
from app.models import ResearchChunk, RetrievedChunk


def _embed(
    client: genai.Client, texts: list[str], task_type: str
) -> np.ndarray:
    """Return unit-length embedding vectors for the given texts."""
    result = client.models.embed_content(
        model=config.EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    vectors = np.array([e.values for e in result.embeddings], dtype=np.float32)
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def _band(score: float) -> str:
    """Sort a similarity score into a coarse high/medium/low label."""
    if score >= config.BAND_HIGH:
        return "high"
    if score >= config.BAND_MEDIUM:
        return "medium"
    return "low"


class ResearchStore:
    """Loads the corpus, embeds it once, and finds the closest documents."""

    def __init__(self, corpus_dir: Path, client: genai.Client):
        self._chunks = [
            ResearchChunk(**json.loads(path.read_text()))
            for path in sorted(Path(corpus_dir).glob("*.json"))
        ]
        texts = [chunk.text for chunk in self._chunks]
        self._vectors = _embed(client, texts, "RETRIEVAL_DOCUMENT")
        self._client = client

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        """Return the top_k chunks most similar to the query, best first."""
        query_vector = _embed(self._client, [query], "RETRIEVAL_QUERY")[0]
        scores = self._vectors @ query_vector
        best = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievedChunk(self._chunks[i], float(scores[i]), _band(scores[i]))
            for i in best
        ]
