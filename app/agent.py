"""Talks to the model and streams back its reply."""

from collections.abc import Iterator

from google import genai
from google.genai import types

from app import config


def message(role: str, text: str) -> types.Content:
    """Wrap a line of text as a conversation turn."""
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


def run_turn(
    contents: list[types.Content], client: genai.Client
) -> Iterator[str]:
    """Send the conversation and stream the reply back piece by piece."""
    stream = client.models.generate_content_stream(
        model=config.MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            max_output_tokens=config.MAX_TOKENS
        ),
    )
    for chunk in stream:
        if chunk.text:  # some chunks arrive without any text
            yield chunk.text
