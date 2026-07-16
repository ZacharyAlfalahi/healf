"""Exact, field-based search over the product catalogue."""

import json
from pathlib import Path

from app.models import Product


class ProductStore:
    """Loads the catalogue and finds products by ingredient, name or tag."""

    def __init__(self, catalogue_path: Path):
        raw = json.loads(Path(catalogue_path).read_text())
        self._products = [Product(**item) for item in raw]

    def search(self, ingredient: str) -> list[Product]:
        """Return products whose name, ingredients or tags contain the term."""
        term = ingredient.lower()
        return [
            product
            for product in self._products
            if term in product.name.lower()
            or any(term in i.lower() for i in product.ingredients)
            or any(term in t.lower() for t in product.tags)
        ]

    def get_prices(self, product_ids: list[str]) -> dict[str, float]:
        """Look up the price of each given product id."""
        by_id = {product.id: product.price for product in self._products}
        return {pid: by_id[pid] for pid in product_ids if pid in by_id}
