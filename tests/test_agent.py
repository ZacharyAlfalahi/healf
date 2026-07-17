"""Structural checks for the agent loop's context handling."""

from google.genai import types

from app import agent
from app.agent import forget_evidence, message, run_turn


def _call(name: str, **args) -> types.Part:
    return types.Part(function_call=types.FunctionCall(name=name, args=args))


def _result(name: str, response: dict) -> types.Content:
    """A tool turn carrying a result, as ``run_turn`` records it."""
    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(name=name, response=response)],
    )


def _texts(contents: list[types.Content]) -> list[tuple[str, str]]:
    """The (role, text) of every text part left in the history."""
    return [
        (content.role, part.text)
        for content in contents
        for part in content.parts or []
        if part.text
    ]


def _has_tool_traffic(contents: list[types.Content]) -> bool:
    return any(
        part.function_call or part.function_response
        for content in contents
        for part in content.parts or []
    )


def test_forget_evidence_keeps_only_conversation_text():
    """A finished turn collapses to the question and the reply."""
    contents = [
        message("user", "why am I fatigued?"),
        types.Content(role="model", parts=[_call("search_research", query="iron")]),
        _result("search_research", {"results": [{"text": "iron helps"}]}),
        message("model", "Low ferritin can drain energy."),
    ]

    forget_evidence(contents, 0)

    assert _texts(contents) == [
        ("user", "why am I fatigued?"),
        ("model", "Low ferritin can drain energy."),
    ]
    assert not _has_tool_traffic(contents)


def test_forget_evidence_keeps_prose_streamed_with_a_call():
    """Prose the model streamed alongside a call survives; the call is dropped."""
    contents = [
        message("user", "why am I fatigued?"),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="Let me check the research."),
                _call("search_research", query="iron"),
            ],
        ),
        _result("search_research", {"results": []}),
        message("model", "Low ferritin can drain energy."),
    ]

    forget_evidence(contents, 0)

    assert _texts(contents) == [
        ("user", "why am I fatigued?"),
        ("model", "Let me check the research."),
        ("model", "Low ferritin can drain energy."),
    ]
    assert not _has_tool_traffic(contents)


def test_forget_evidence_leaves_earlier_turns_untouched():
    """Only the current turn's evidence is dropped; prior text stays."""
    contents = [
        message("user", "what did my panel flag?"),
        message("model", "Low ferritin."),
        message("user", "what should I take?"),
        types.Content(role="model", parts=[_call("search_products", ingredient="iron")]),
        _result("search_products", {"products": [{"id": "p1"}]}),
        message("model", "Look at iron with vitamin C."),
    ]

    forget_evidence(contents, 2)  # mark = start of this turn's user message

    assert _texts(contents) == [
        ("user", "what did my panel flag?"),
        ("model", "Low ferritin."),
        ("user", "what should I take?"),
        ("model", "Look at iron with vitamin C."),
    ]


# --- Driver-level: exercise run_turn against a scripted fake client ---


class _Stub:
    """Attribute bag standing in for a streamed chunk's nested objects."""

    def __init__(self, **fields):
        self.__dict__.update(fields)


def _chunk(*parts: types.Part) -> _Stub:
    return _Stub(candidates=[_Stub(content=_Stub(parts=list(parts)))])


class _FakeModels:
    def __init__(self, scripts):
        self._scripts = list(scripts)
        self.seen: list[list[types.Content]] = []

    def generate_content_stream(self, model, contents, config):
        self.seen.append(list(contents))  # contents as of this stream call
        return self._scripts.pop(0)


class _FakeClient:
    def __init__(self, scripts):
        self.models = _FakeModels(scripts)


def test_run_turn_keeps_prose_streamed_before_a_tool_call(monkeypatch):
    """A model turn that narrates then calls a tool keeps both in history."""
    monkeypatch.setattr(agent, "dispatch", lambda *a, **k: {"results": []})
    client = _FakeClient(
        [
            [_chunk(types.Part.from_text(text="Let me check the research."),
                    _call("search_research", query="iron"))],
            [_chunk(types.Part.from_text(text="Iron may help your energy."))],
        ]
    )
    contents = [message("user", "why am I tired?")]

    streamed = "".join(
        run_turn(contents, client, None, "system", lambda _: None)
    )

    # The preamble was shown to the customer...
    assert "Let me check the research." in streamed
    # ...and it is recorded in history, not dropped with the tool call.
    model_text = " ".join(t for role, t in _texts(contents) if role == "model")
    assert "Let me check the research." in model_text
    assert "Iron may help your energy." in model_text

    # After the turn, evidence is gone but both pieces of prose remain.
    forget_evidence(contents, 0)
    assert _texts(contents) == [
        ("user", "why am I tired?"),
        ("model", "Let me check the research."),
        ("model", "Iron may help your energy."),
    ]
    assert not _has_tool_traffic(contents)
