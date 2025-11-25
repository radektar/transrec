"""Tests for summarizer module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.summarizer import BaseSummarizer, ClaudeSummarizer, get_summarizer
from src.config import config


class TestBaseSummarizer:
    """Test base summarizer interface."""
    
    def test_base_summarizer_is_abstract(self):
        """Test that BaseSummarizer cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseSummarizer()


class TestClaudeSummarizer:
    """Test Claude summarizer implementation."""
    
    @pytest.fixture
    def mock_anthropic(self):
        """Mock Anthropic client."""
        with patch('src.summarizer.Anthropic') as mock:
            client_instance = MagicMock()
            mock.return_value = client_instance
            yield client_instance
    
    @pytest.fixture
    def summarizer(self, mock_anthropic):
        """Create ClaudeSummarizer instance with mocked client."""
        return ClaudeSummarizer(api_key="test-key", model="claude-3-haiku-20240307")
    
    def test_claude_summarizer_initialization(self, summarizer):
        """Test ClaudeSummarizer initializes correctly."""
        assert summarizer.model == "claude-3-haiku-20240307"
        assert summarizer.max_words == config.SUMMARY_MAX_WORDS
        assert summarizer.title_max_length == config.TITLE_MAX_LENGTH
    
    def test_claude_summarizer_missing_package(self):
        """Test error when anthropic package is missing."""
        with patch.dict('sys.modules', {'anthropic': None}):
            with pytest.raises(ImportError):
                ClaudeSummarizer(api_key="test-key")
    
    def test_generate_success(self, summarizer, mock_anthropic):
        """Test successful summary generation."""
        # Mock API response with enhanced markdown format
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = (
            "TITLE: Rozmowa o projekcie\n\n"
            "SUMMARY: ## Podsumowanie\n\n"
            "Dyskusja na temat implementacji **nowych funkcji**. "
            "Omówiono kluczowe aspekty projektu.\n\n"
            "## Kluczowe punkty\n\n"
            "⚠️ **Krytyczne:**\n"
            "- Decyzja o terminie wdrożenia\n\n"
            "⚡ **Ważne:**\n"
            "- Monitorowanie postępów\n\n"
            "📝 **Informacyjne:**\n"
            "- Kontekst projektu\n\n"
            "## Cytaty\n\n"
            "### Temat: Wdrożenie\n"
            "> \"Musimy to wdrożyć do końca miesiąca\"\n"
            "> — *Kontekst: Dyskusja o terminach*\n\n"
            "## Lista działań (To-do)\n\n"
            "- Przygotować dokumentację\n"
            "- Skontaktować się z zespołem"
        )
        mock_anthropic.messages.create.return_value = mock_response
        
        transcript = "To jest przykładowa transkrypcja nagrania."
        result = summarizer.generate(transcript)
        
        assert "title" in result
        assert "summary" in result
        assert result["title"] == "Rozmowa o projekcie"
        assert "## Podsumowanie" in result["summary"]
        assert "## Kluczowe punkty" in result["summary"]
        assert "## Cytaty" in result["summary"]
        assert "## Lista działań (To-do)" in result["summary"]
        assert "⚠️" in result["summary"]
        assert "⚡" in result["summary"]
        assert "📝" in result["summary"]
        assert "Dyskusja" in result["summary"]
        mock_anthropic.messages.create.assert_called_once()
    
    def test_generate_empty_transcript(self, summarizer):
        """Test handling of empty transcript."""
        result = summarizer.generate("")
        
        assert "title" in result
        assert "summary" in result
        assert result["title"] == "Nagranie"
        # Fallback summary should include markdown structure with all sections
        assert "## Podsumowanie" in result["summary"]
        assert "## Kluczowe punkty" in result["summary"]
        assert "## Cytaty" in result["summary"]
        assert "## Lista działań (To-do)" in result["summary"]
        assert "⚠️" in result["summary"]
        assert "⚡" in result["summary"]
        assert "📝" in result["summary"]
    
    def test_generate_long_transcript_truncation(self, summarizer, mock_anthropic):
        """Test that long transcripts are truncated."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = (
            "TITLE: Test\n\n"
            "SUMMARY: ## Podsumowanie\n\nTest summary\n\n"
            "## Lista działań (To-do)\n\n- Task 1"
        )
        mock_anthropic.messages.create.return_value = mock_response
        
        # Create very long transcript
        long_transcript = "A" * 20000
        result = summarizer.generate(long_transcript)
        
        # Should still succeed
        assert "title" in result
        assert "## Podsumowanie" in result["summary"]
        # Verify truncation happened (check call args)
        call_args = mock_anthropic.messages.create.call_args
        prompt_text = call_args[1]["messages"][0]["content"]
        assert len(prompt_text) < len(long_transcript)
    
    def test_generate_api_error_fallback(self, summarizer, mock_anthropic):
        """Test fallback when API call fails."""
        mock_anthropic.messages.create.side_effect = Exception("API Error")
        
        transcript = "Test transcript"
        result = summarizer.generate(transcript)
        
        # Should return fallback summary with markdown structure including all sections
        assert "title" in result
        assert "summary" in result
        assert result["title"] == "Test transcript"
        assert "## Podsumowanie" in result["summary"]
        assert "## Kluczowe punkty" in result["summary"]
        assert "## Cytaty" in result["summary"]
        assert "## Lista działań (To-do)" in result["summary"]
        assert "⚠️" in result["summary"]
        assert "⚡" in result["summary"]
        assert "📝" in result["summary"]
    
    def test_title_length_limit(self, summarizer, mock_anthropic):
        """Test that title is truncated to max length."""
        long_title = "A" * 200
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = (
            f"TITLE: {long_title}\n\n"
            "SUMMARY: ## Podsumowanie\n\nTest\n\n"
            "## Lista działań (To-do)\n\n- Task 1"
        )
        mock_anthropic.messages.create.return_value = mock_response
        
        result = summarizer.generate("Test")
        
        assert len(result["title"]) <= config.TITLE_MAX_LENGTH
    
    def test_parse_response_standard_format(self, summarizer):
        """Test parsing of standard response format with markdown."""
        response = (
            "TITLE: Test Title\n\n"
            "SUMMARY: ## Podsumowanie\n\n"
            "Test summary text here.\n\n"
            "## Kluczowe punkty\n\n"
            "⚠️ **Krytyczne:**\n"
            "- Test point\n\n"
            "## Cytaty\n\n"
            "### Temat: Test\n"
            "> \"Test quote\"\n\n"
            "## Lista działań (To-do)\n\n"
            "- Przygotować dokumentację\n"
            "- Skontaktować się z zespołem"
        )
        title, summary = summarizer._parse_response(response)
        
        assert title == "Test Title"
        assert "## Podsumowanie" in summary
        assert "## Kluczowe punkty" in summary
        assert "## Cytaty" in summary
        assert "## Lista działań (To-do)" in summary
        assert "Test summary" in summary
    
    def test_parse_response_fallback(self, summarizer):
        """Test parsing fallback for non-standard format."""
        response = "Some text\n\nMore text here"
        title, summary = summarizer._parse_response(response)
        
        assert title
        assert summary
        # Fallback should include markdown structure
        assert "## Podsumowanie" in summary
    
    def test_summary_markdown_structure(self, summarizer, mock_anthropic):
        """Test that summary contains proper markdown structure with all sections."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = (
            "TITLE: Spotkanie projektowe\n\n"
            "SUMMARY: ## Podsumowanie\n\n"
            "Podczas spotkania omówiono **kluczowe aspekty** projektu. "
            "Zidentyfikowano główne wyzwania i możliwości rozwoju. "
            "Ustalone zostały priorytety na najbliższe tygodnie.\n\n"
            "## Kluczowe punkty\n\n"
            "⚠️ **Krytyczne:**\n"
            "- Ustalenie terminów wdrożenia\n\n"
            "⚡ **Ważne:**\n"
            "- Monitorowanie postępów\n\n"
            "📝 **Informacyjne:**\n"
            "- Kontekst projektu\n\n"
            "## Cytaty\n\n"
            "### Temat: Priorytety\n"
            "> \"Musimy ustalić priorytety na najbliższe tygodnie\"\n"
            "> — *Kontekst: Dyskusja o planowaniu*\n\n"
            "## Lista działań (To-do)\n\n"
            "- Przygotować szczegółową dokumentację techniczną\n"
            "- Skontaktować się z zespołem deweloperskim\n"
            "- Zaplanować kolejne spotkanie"
        )
        mock_anthropic.messages.create.return_value = mock_response
        
        result = summarizer.generate("Test transcript")
        
        # Verify structure with all new sections
        assert "## Podsumowanie" in result["summary"]
        assert "## Kluczowe punkty" in result["summary"]
        assert "## Cytaty" in result["summary"]
        assert "## Lista działań (To-do)" in result["summary"]
        # Verify emoji are present
        assert "⚠️" in result["summary"]
        assert "⚡" in result["summary"]
        assert "📝" in result["summary"]
        # Verify summary content
        assert "omówiono" in result["summary"] or "Podczas" in result["summary"]
        # Verify to-do list items
        assert "- Przygotować" in result["summary"] or "Przygotować" in result["summary"]
        assert "- Skontaktować" in result["summary"] or "Skontaktować" in result["summary"]


class TestGetSummarizer:
    """Test summarizer factory function."""
    
    def test_get_summarizer_disabled(self, monkeypatch):
        """Test that None is returned when summarization is disabled."""
        monkeypatch.setattr(config, 'ENABLE_SUMMARIZATION', False)
        
        result = get_summarizer()
        assert result is None
    
    def test_get_summarizer_claude_no_key(self, monkeypatch):
        """Test that None is returned when Claude key is missing."""
        monkeypatch.setattr(config, 'ENABLE_SUMMARIZATION', True)
        monkeypatch.setattr(config, 'LLM_PROVIDER', 'claude')
        monkeypatch.setattr(config, 'LLM_API_KEY', None)
        
        result = get_summarizer()
        assert result is None
    
    @patch('src.summarizer.ClaudeSummarizer')
    def test_get_summarizer_claude_success(self, mock_claude, monkeypatch):
        """Test successful Claude summarizer creation."""
        monkeypatch.setattr(config, 'ENABLE_SUMMARIZATION', True)
        monkeypatch.setattr(config, 'LLM_PROVIDER', 'claude')
        monkeypatch.setattr(config, 'LLM_API_KEY', 'test-key')
        monkeypatch.setattr(config, 'LLM_MODEL', 'claude-3-haiku-20240307')
        
        mock_instance = MagicMock()
        mock_claude.return_value = mock_instance
        
        result = get_summarizer()
        
        assert result is not None
        mock_claude.assert_called_once_with(
            api_key='test-key',
            model='claude-3-haiku-20240307'
        )
    
    def test_get_summarizer_unknown_provider(self, monkeypatch):
        """Test handling of unknown provider."""
        monkeypatch.setattr(config, 'ENABLE_SUMMARIZATION', True)
        monkeypatch.setattr(config, 'LLM_PROVIDER', 'unknown')
        
        result = get_summarizer()
        assert result is None

