"""Tool declarations and the dispatch that runs them against the stores."""

from dataclasses import dataclass

from google.genai import types

from app import config
from app.product_store import ProductStore
from app.research_store import ResearchStore


@dataclass
class Stores:
    """The knowledge sources a tool call can reach."""

    research: ResearchStore
    products: ProductStore


_RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "What to look for, e.g. 'iron and fatigue'.",
        }
    },
    "required": ["query"],
}

_PRODUCTS_SCHEMA = {
    "type": "object",
    "properties": {
        "ingredient": {
            "type": "string",
            "description": "An ingredient, name, or tag, e.g. 'iron'.",
        }
    },
    "required": ["ingredient"],
}

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_research",
                description=(
                    "Search the wellness research library for evidence on "
                    "a health or nutrition topic."
                ),
                parameters_json_schema=_RESEARCH_SCHEMA,
            ),
            types.FunctionDeclaration(
                name="search_products",
                description=(
                    "Find products in the catalogue by ingredient, name, "
                    "or tag."
                ),
                parameters_json_schema=_PRODUCTS_SCHEMA,
            ),
        ]
    )
]


def dispatch(name: str, args: dict, stores: Stores) -> dict:
    """Run a tool call and return a JSON-serialisable result."""
    if name == "search_research":
        hits = stores.research.search(args.get("query", ""), config.TOP_K)
        return {
            "results": [
                {
                    "title": hit.chunk.title,
                    "source": hit.chunk.source,
                    "text": hit.chunk.text,
                    "relevance": hit.band,
                }
                for hit in hits
            ]
        }
    if name == "search_products":
        found = stores.products.search(args.get("ingredient", ""))
        # Price is deliberately left out so it never reaches the model.
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "pillar": product.pillar,
                    "ingredients": product.ingredients,
                    "tags": product.tags,
                    "description": product.description,
                }
                for product in found
            ]
        }
    return {"error": f"unknown tool: {name}"}
