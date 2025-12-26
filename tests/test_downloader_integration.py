"""Integration tests for dependency downloader.

Uwaga: Te testy wymagają połączenia z internetem i są wolne.
Uruchamiaj tylko przed merge do develop.
"""

import pytest

from src.setup.downloader import DependencyDownloader
from src.setup.errors import NetworkError


class TestDownloaderIntegration:
    """Testy integracyjne dla DependencyDownloader."""

    @pytest.fixture
    def downloader(self):
        """Fixture tworzący downloader."""
        return DependencyDownloader()

    @pytest.mark.slow
    @pytest.mark.integration
    def test_download_whisper_real(self, downloader):
        """Test prawdziwego pobierania whisper-cli z GitHub."""
        # Skip jeśli brak internetu
        try:
            downloader.check_network()
        except NetworkError:
            pytest.skip("Brak połączenia z internetem")
        
        # Skip jeśli już zainstalowany
        if downloader.is_whisper_installed():
            pytest.skip("whisper-cli już zainstalowany")
        
        # TODO: Odkomentuj po utworzeniu GitHub Release
        # downloader.download_whisper()
        # assert downloader.is_whisper_installed()

    @pytest.mark.slow
    @pytest.mark.integration
    def test_download_ffmpeg_real(self, downloader):
        """Test prawdziwego pobierania ffmpeg."""
        # Skip jeśli brak internetu
        try:
            downloader.check_network()
        except NetworkError:
            pytest.skip("Brak połączenia z internetem")
        
        # Skip jeśli już zainstalowany
        if downloader.is_ffmpeg_installed():
            pytest.skip("ffmpeg już zainstalowany")
        
        # TODO: Odkomentuj po utworzeniu GitHub Release
        # downloader.download_ffmpeg()
        # assert downloader.is_ffmpeg_installed()

    @pytest.mark.slow
    @pytest.mark.integration
    def test_verify_checksum_real(self, downloader, tmp_path):
        """Test weryfikacji checksum na prawdziwym pliku."""
        # Utwórz plik testowy
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content for checksum")
        
        # Oblicz SHA256
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update(b"test content for checksum")
        expected_checksum = sha256.hexdigest()
        
        # Weryfikuj
        assert downloader.verify_checksum(test_file, expected_checksum) is True
        assert downloader.verify_checksum(test_file, "wrong" * 16) is False

