"""Deterministic tests for product search and relevance banding."""

from app import config
from app.research_store import _band


def test_search_finds_iron_skus(products):
    ids = {product.id for product in products.search("iron")}
    assert {"iron-vitc", "iron-only"} <= ids


def test_search_is_case_insensitive(products):
    assert products.search("IRON") == products.search("iron")


def test_search_matches_a_substring_inside_an_ingredient(products):
    # "ferrous" sits inside "iron (ferrous bisglycinate)".
    ids = {product.id for product in products.search("ferrous")}
    assert {"iron-vitc", "iron-only"} <= ids


def test_search_matches_tags(products):
    ids = {product.id for product in products.search("vegan_ok")}
    assert "creatine" in ids


def test_search_with_no_match_returns_empty(products):
    assert products.search("unobtanium") == []


def test_search_with_blank_term_returns_empty(products):
    assert products.search("   ") == []


def test_get_prices_returns_known_and_skips_unknown(products):
    prices = products.get_prices(["iron-vitc", "iron-only", "made-up"])
    assert prices["iron-vitc"] > 0
    assert prices["iron-only"] > 0
    assert "made-up" not in prices


def test_get_prices_of_nothing_is_empty(products):
    assert products.get_prices([]) == {}


def test_bands_follow_the_configured_cutoffs():
    assert _band(1.0) == "high"
    assert _band(config.BAND_HIGH) == "high"
    assert _band(config.BAND_HIGH - 0.01) == "medium"
    assert _band(config.BAND_MEDIUM) == "medium"
    assert _band(config.BAND_MEDIUM - 0.01) == "low"
    assert _band(0.0) == "low"
