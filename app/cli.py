"""Interactive chat loop for the command line."""

import json

from google import genai
from google.genai import errors, types

from app import config, prompts
from app.agent import message, run_turn
from app.product_store import ProductStore
from app.research_store import ResearchStore
from app.tools import Stores


def _status_line(text: str) -> None:
    """Print a status line while the model is using a tool."""
    print(f"↳ {text}", flush=True)


def main() -> None:
    """Read a question, stream the answer, and repeat until the user quits."""
    client = genai.Client(api_key=config.get_api_key())
    profile = json.loads(config.CUSTOMER_PATH.read_text())
    instruction = prompts.system_instruction(profile)

    try:
        stores = Stores(
            research=ResearchStore(config.CORPUS_DIR, client),
            products=ProductStore(config.PRODUCTS_PATH),
        )
    except errors.APIError as error:
        print(f"Couldn't start up: {error.message}")
        return

    contents: list[types.Content] = []
    print("Healf wellness assistant (Ctrl-C or Ctrl-D to exit).\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        mark = len(contents)
        contents.append(message("user", user_input))
        started = False
        try:
            for token in run_turn(
                contents, client, stores, instruction, _status_line
            ):
                if not started:
                    print("Assistant: ", end="", flush=True)
                    started = True
                print(token, end="", flush=True)
        except KeyboardInterrupt:
            print("\n[interrupted]\n")
            del contents[mark:]
            continue
        except errors.APIError as error:
            print(f"\n[model unavailable: {error.message}]\n")
            del contents[mark:]
            continue

        print("\n")


if __name__ == "__main__":
    main()
