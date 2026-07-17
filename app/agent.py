"""Talks to the model, resolving tool calls and streaming the final reply."""

from collections.abc import Callable, Iterator

from google import genai
from google.genai import types

from app import config
from app.tools import TOOLS, Stores, dispatch


def message(role: str, text: str) -> types.Content:
    """Wrap a line of text as a conversation turn."""
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


def run_turn(
    contents: list[types.Content],
    client: genai.Client,
    stores: Stores,
    system_instruction: str,
    on_tool: Callable[[str], None],
) -> Iterator[str]:
    """Run the model until it answers, streaming the final reply.

    Tool calls are resolved along the way and the whole exchange is recorded
    in ``contents``. ``on_tool`` receives a short status line for each search.
    """
    settings = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=TOOLS,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        max_output_tokens=config.MAX_TOKENS,
    )
    for _ in range(config.MAX_ITERS):
        tool_parts: list[types.Part] = []
        answer = ""
        stream = client.models.generate_content_stream(
            model=config.MODEL, contents=contents, config=settings
        )
        for chunk in stream:
            for part in _parts(chunk):
                if part.function_call:
                    tool_parts.append(part)
                elif part.text:
                    answer += part.text
                    yield part.text
        if not tool_parts:
            contents.append(message("model", answer))
            return
        # Keep the original parts so their thought signatures survive.
        contents.append(types.Content(role="model", parts=tool_parts))
        for part in tool_parts:
            call = part.function_call
            on_tool(_status(call.name))
            result = dispatch(call.name, dict(call.args), stores)
            contents.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=call.name, response=result
                        )
                    ],
                )
            )
    stalled = "Sorry, I couldn't pull that together. Could you rephrase?"
    contents.append(message("model", stalled))
    yield stalled


def _parts(chunk) -> list:
    """Return the content parts of a streamed chunk, or an empty list."""
    candidate = chunk.candidates[0] if chunk.candidates else None
    if candidate and candidate.content:
        return candidate.content.parts or []
    return []


def _status(tool_name: str) -> str:
    """A short, human-readable line describing a tool call."""
    if tool_name == "search_research":
        return "searching the research library…"
    if tool_name == "search_products":
        return "looking through the catalogue…"
    return f"running {tool_name}…"
