"""Talks to the model, resolving tool calls and streaming the final reply."""

from collections.abc import Callable, Iterator

from google import genai
from google.genai import types

from app import config
from app.tools import TOOLS, Stores, dispatch


def message(role: str, text: str) -> types.Content:
    """Wrap a line of text as a conversation turn."""
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


def _text_only(content: types.Content) -> types.Content | None:
    """A turn stripped to its text parts, or ``None`` if it had none.

    Tool calls and their results are dropped; any prose the model streamed
    alongside a call is kept, so nothing the customer saw leaves the history.
    """
    text = [part for part in content.parts or [] if part.text]
    if not text:
        return None
    return types.Content(role=content.role, parts=text)


def forget_evidence(contents: list[types.Content], start: int) -> None:
    """Drop tool traffic from ``contents[start:]``, keeping conversation text.

    Retrieved evidence lives only for the turn that fetched it; the running
    history keeps just the user's questions and the assistant's replies.
    """
    kept = (_text_only(content) for content in contents[start:])
    contents[start:] = [content for content in kept if content is not None]


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
        temperature=config.TEMPERATURE,
    )
    # Same settings with the tools removed, for the forced closing answer.
    no_tools = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )
    for _ in range(config.MAX_ITERS):
        parts, answer = yield from _stream(client, contents, settings)
        tool_parts = [part for part in parts if part.function_call]
        if not tool_parts:
            contents.append(message("model", answer))
            return
        # Record the turn as streamed — any prose alongside the calls, and the
        # calls' thought signatures — so the history matches what was said.
        contents.append(types.Content(role="model", parts=parts))
        for part in tool_parts:
            call = part.function_call
            on_tool(_status(call.name))
            result = dispatch(call.name, dict(call.args or {}), stores)
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
    # Tool budget spent: make one last pass with tools off to force an answer
    # from the evidence already gathered, rather than stranding it unanswered.
    _, answer = yield from _stream(client, contents, no_tools)
    if answer.strip():
        contents.append(message("model", answer))
        return
    stalled = "Sorry, I couldn't pull that together. Could you rephrase?"
    contents.append(message("model", stalled))
    yield stalled


def _stream(
    client: genai.Client,
    contents: list[types.Content],
    settings: types.GenerateContentConfig,
) -> Iterator[str]:
    """Stream one model turn. Yields text; returns (parts, answer).

    ``parts`` are the streamed content parts in order — text and tool calls
    alike — so the caller can record the turn exactly as the model produced it.
    """
    parts: list[types.Part] = []
    answer = ""
    stream = client.models.generate_content_stream(
        model=config.MODEL, contents=contents, config=settings
    )
    for chunk in stream:
        for part in _parts(chunk):
            if part.function_call:
                parts.append(part)
            elif part.text:
                parts.append(part)
                answer += part.text
                yield part.text
    return parts, answer


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
