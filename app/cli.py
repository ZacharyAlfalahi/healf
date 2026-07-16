"""Interactive chat loop for the command line."""

from google import genai
from google.genai import errors, types

from app import config
from app.agent import message, run_turn


def main() -> None:
    """Read a question, stream the answer, and repeat until the user quits."""
    client = genai.Client(api_key=config.get_api_key())
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

        contents.append(message("user", user_input))

        print("Assistant: ", end="", flush=True)
        reply_parts: list[str] = []
        try:
            for token in run_turn(contents, client):
                print(token, end="", flush=True)
                reply_parts.append(token)
        except KeyboardInterrupt:
            # Drop the unanswered turn so the history stays in order.
            print("\n[interrupted]\n")
            contents.pop()
            continue
        except errors.APIError as error:
            # Show what went wrong instead of a stack trace, then carry on.
            print(f"\n[model unavailable: {error.message}]\n")
            contents.pop()
            continue

        print("\n")
        contents.append(message("model", "".join(reply_parts)))


if __name__ == "__main__":
    main()
