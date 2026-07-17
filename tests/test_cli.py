"""Offline checks for the CLI's startup handling."""

from app import cli, config


def _raise_missing_key() -> str:
    raise RuntimeError("Set GEMINI_API_KEY (or GOOGLE_API_KEY).")


def test_missing_key_exits_without_traceback(monkeypatch, capsys):
    """A missing key is a friendly startup message, not a traceback."""
    monkeypatch.setattr(config, "get_api_key", _raise_missing_key)

    cli.main()  # returns before the input loop; must not raise

    assert "Couldn't start up" in capsys.readouterr().out
