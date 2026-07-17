"""Checks that the mock data is well-formed and demo-ready."""

CORPUS_IDS = {
    "iron-deficiency-fatigue",
    "vitamin-c-iron-absorption",
    "iron-endurance-athletes",
    "vegetarian-iron-sources",
    "creatine-vegetarians",
    "protein-recovery",
    "sleep-recovery",
}
CHUNK_FIELDS = {"id", "title", "source", "topic", "text"}
PRODUCT_FIELDS = {
    "id", "name", "pillar", "ingredients", "tags", "description", "price"
}
REQUIRED_SKUS = {
    "iron-vitc",
    "iron-only",
    "vitamin-c",
    "creatine",
    "whey-protein",
    "plant-protein",
}


def test_corpus_has_the_seven_expected_docs(corpus_docs):
    ids = [doc["id"] for doc in corpus_docs]
    assert len(ids) == 7
    assert set(ids) == CORPUS_IDS
    assert len(ids) == len(set(ids))


def test_every_corpus_doc_is_complete(corpus_docs):
    for doc in corpus_docs:
        assert CHUNK_FIELDS <= set(doc)
        assert doc["text"].strip()


def test_catalogue_is_well_formed(catalogue):
    ids = [product["id"] for product in catalogue]
    assert len(ids) >= 12
    assert len(ids) == len(set(ids))
    assert REQUIRED_SKUS <= set(ids)
    for product in catalogue:
        assert PRODUCT_FIELDS <= set(product)
        assert isinstance(product["ingredients"], list)
        assert isinstance(product["price"], (int, float))
        assert product["price"] > 0


def test_iron_skus_are_searchable_by_iron_and_ferrous(catalogue):
    for sku in ("iron-vitc", "iron-only"):
        product = next(p for p in catalogue if p["id"] == sku)
        ingredients = " ".join(product["ingredients"]).lower()
        assert "iron" in ingredients
        assert "ferrous" in ingredients


def test_customer_profile_matches_the_persona(profile):
    assert profile["sex"] == "female"
    assert "vegetarian" in profile["diet"].lower()
    ferritin = profile["biomarkers"]["ferritin"]
    assert ferritin["value"] == 18
    assert ferritin["flag"] == "low"
