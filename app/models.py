"""Typed records for the research corpus and the product catalogue."""

from dataclasses import dataclass


@dataclass
class ResearchChunk:
    """One research document from the corpus."""

    id: str
    title: str
    source: str
    topic: str
    text: str


@dataclass
class RetrievedChunk:
    """A research chunk returned by a search, with its similarity and band."""

    chunk: ResearchChunk
    score: float
    band: str  # "high", "medium", or "low"


@dataclass
class Product:
    """One item in the product catalogue."""

    id: str
    name: str
    pillar: str
    ingredients: list[str]
    tags: list[str]
    description: str
    price: float
