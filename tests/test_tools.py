"""Tests for tool dispatch, especially that price never leaves the store."""

from app.models import ResearchChunk, RetrievedChunk
from app.tools import Stores, dispatch


class _FakeResearch:
    """A stand-in research store with a fixed result, so no API is needed."""

    def __init__(self, hits):
        self._hits = hits

    def search(self, query, top_k):
        return self._hits[:top_k]


def _stores(products):
    chunk = ResearchChunk("x", "Title", "Source", "topic", "body text")
    research = _FakeResearch([RetrievedChunk(chunk, 0.8, "high")])
    return Stores(research=research, products=products)


def test_search_products_never_includes_price(products):
    result = dispatch(
        "search_products", {"ingredient": "iron"}, _stores(products)
    )
    assert result["products"]
    for product in result["products"]:
        assert "price" not in product
        assert set(product) == {
            "id", "name", "pillar", "ingredients", "tags", "description"
        }


def test_search_research_returns_text_and_band(products):
    result = dispatch("search_research", {"query": "iron"}, _stores(products))
    assert result["results"]
    hit = result["results"][0]
    assert set(hit) == {"title", "source", "text", "relevance"}
    assert hit["relevance"] == "high"


def test_missing_arguments_do_not_crash(products):
    assert dispatch("search_products", {}, _stores(products))["products"] == []


def test_unknown_tool_returns_an_error(products):
    assert "error" in dispatch("no_such_tool", {}, _stores(products))
