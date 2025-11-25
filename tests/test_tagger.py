"""Tests for tagger module."""

from unittest.mock import MagicMock

from src import tagger as tagger_module
from src.config import Config
from src.tagger import ClaudeTagger


def _patch_anthropic(monkeypatch, response_text: str) -> None:
    """Patch Anthropic client used by ClaudeTagger to return response_text."""

    class FakeMessages:
        def __init__(self, text: str) -> None:
            self._text = text

        def create(self, *_, **__):
            chunk = type("Chunk", (), {"text": self._text})()
            return type("Message", (), {"content": [chunk]})()

    class FakeClient:
        def __init__(self, *_args, **_kwargs) -> None:
            self.messages = FakeMessages(response_text)

    monkeypatch.setattr(tagger_module, "Anthropic", FakeClient)


def test_claude_tagger_parses_json(monkeypatch):
    """ClaudeTagger should parse unique tags from JSON response."""
    _patch_anthropic(monkeypatch, '["sauna", "zdrowie", "sauna"]')
    monkeypatch.setattr(tagger_module.config, "ENABLE_LLM_TAGGING", True)

    tagger = ClaudeTagger(api_key="test", model="claude-test")

    tags = tagger.generate_tags(
        transcript="To jest przykładowa transkrypcja.",
        summary_markdown="## Podsumowanie\n\nTreść",
        existing_tags=["sauna"],
    )

    assert isinstance(tags, list)
    assert "sauna" in tags
    assert len(tags) <= Config().MAX_TAGS_PER_NOTE


def test_claude_tagger_invalid_json_returns_empty(monkeypatch):
    """Invalid JSON should result in empty tag list."""
    _patch_anthropic(monkeypatch, "Brak JSON")
    monkeypatch.setattr(tagger_module.config, "ENABLE_LLM_TAGGING", True)

    tagger = ClaudeTagger(api_key="test", model="claude-test")

    tags = tagger.generate_tags("Test", "Summary", [])

    assert tags == []

