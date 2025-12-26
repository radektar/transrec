"""Dependency downloader for whisper.cpp and ffmpeg."""

import hashlib
import platform
import shutil
import socket
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.logger import logger
from src.setup.checksums import CHECKSUMS, SIZES, URLS
from src.setup.errors import (
    ChecksumError,
    DiskSpaceError,
    DownloadError,
    NetworkError,
)

# Minimalna ilość miejsca na dysku (500MB)
MIN_DISK_SPACE_BYTES = 500_000_000

# Timeouty
CHUNK_TIMEOUT = 30  # sekundy
TOTAL_TIMEOUT = 1800  # 30 minut dla dużego modelu
MAX_RETRIES = 3


class DependencyDownloader:
    """Pobieranie i weryfikacja zależności."""

    def __init__(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ):
        """Inicjalizacja downloadera.

        Args:
            progress_callback: Funkcja wywoływana z postępem pobierania.
                               Przyjmuje (name: str, progress: float 0.0-1.0)
        """
        self.progress_callback = progress_callback
        self.support_dir = (
            Path.home() / "Library" / "Application Support" / "Transrec"
        )
        self.bin_dir = self.support_dir / "bin"
        self.models_dir = self.support_dir / "models"
        self.downloads_dir = self.support_dir / "downloads"

        # Utwórz katalogi
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    def check_network(self) -> bool:
        """Sprawdź czy jest połączenie z internetem.

        Returns:
            True jeśli połączenie dostępne, False w przeciwnym razie

        Raises:
            NetworkError: Jeśli brak połączenia
        """
        try:
            # Próba połączenia z Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            raise NetworkError("Brak połączenia z internetem")

    def check_disk_space(self, required_bytes: int = MIN_DISK_SPACE_BYTES) -> bool:
        """Sprawdź czy jest wystarczająco miejsca na dysku.

        Args:
            required_bytes: Wymagana ilość miejsca w bajtach

        Returns:
            True jeśli jest wystarczająco miejsca

        Raises:
            DiskSpaceError: Jeśli brak miejsca
        """
        stat = shutil.disk_usage(self.support_dir)
        free_bytes = stat.free

        if free_bytes < required_bytes:
            raise DiskSpaceError(
                f"Brak miejsca na dysku. "
                f"Dostępne: {free_bytes / 1_000_000:.1f}MB, "
                f"Wymagane: {required_bytes / 1_000_000:.1f}MB"
            )

        return True

    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Zweryfikuj SHA256 checksum pliku.

        Args:
            file_path: Ścieżka do pliku
            expected_checksum: Oczekiwany checksum SHA256

        Returns:
            True jeśli checksum się zgadza, False w przeciwnym razie
        """
        if not expected_checksum:
            logger.warning(
                f"Brak checksum dla {file_path.name}, pomijam weryfikację"
            )
            return True

        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
        except IOError as e:
            logger.error(f"Błąd podczas czytania pliku {file_path}: {e}")
            return False

        actual_checksum = sha256.hexdigest()
        return actual_checksum == expected_checksum.lower().replace("sha256:", "")

    def is_whisper_installed(self) -> bool:
        """Sprawdź czy whisper.cpp jest zainstalowany.

        Returns:
            True jeśli whisper-cli istnieje i ma rozmiar > 0
        """
        whisper_path = self.bin_dir / "whisper-cli"
        return whisper_path.exists() and whisper_path.stat().st_size > 0

    def is_ffmpeg_installed(self) -> bool:
        """Sprawdź czy ffmpeg jest zainstalowany.

        Returns:
            True jeśli ffmpeg istnieje i ma rozmiar > 0
        """
        ffmpeg_path = self.bin_dir / "ffmpeg"
        return ffmpeg_path.exists() and ffmpeg_path.stat().st_size > 0

    def is_model_installed(self, model: str = "small") -> bool:
        """Sprawdź czy model jest pobrany.

        Args:
            model: Nazwa modelu (default: "small")

        Returns:
            True jeśli model istnieje
        """
        model_path = self.models_dir / f"ggml-{model}.bin"
        return model_path.exists()

    def check_all(self) -> bool:
        """Sprawdź czy wszystkie zależności są zainstalowane.

        Returns:
            True jeśli wszystkie zależności są dostępne
        """
        return (
            self.is_whisper_installed()
            and self.is_ffmpeg_installed()
            and self.is_model_installed()
        )

    def _download_file(
        self,
        url: str,
        dest: Path,
        name: str,
        expected_size: Optional[int] = None,
        expected_checksum: Optional[str] = None,
    ) -> None:
        """Pobierz plik z progress callback i retry logic.

        Args:
            url: URL do pobrania
            dest: Ścieżka docelowa
            name: Nazwa pliku (dla progress callback)
            expected_size: Oczekiwany rozmiar pliku (opcjonalnie)
            expected_checksum: Oczekiwany checksum (opcjonalnie)

        Raises:
            DownloadError: Jeśli pobieranie się nie powiodło
            ChecksumError: Jeśli checksum się nie zgadza
        """
        temp_path = self.downloads_dir / f"{dest.name}.tmp"

        # Sprawdź czy istnieje częściowe pobieranie
        resume_from = 0
        if temp_path.exists():
            resume_from = temp_path.stat().st_size
            if expected_size and resume_from >= expected_size:
                # Plik wydaje się kompletny, sprawdź checksum
                logger.info(f"Znaleziono kompletny plik tymczasowy {temp_path}")
                if expected_checksum and self.verify_checksum(
                    temp_path, expected_checksum
                ):
                    # Przenieś do docelowej lokalizacji
                    temp_path.rename(dest)
                    dest.chmod(0o755)
                    logger.info(f"✓ Pobrano {name}")
                    return
                else:
                    # Uszkodzony, usuń i zacznij od nowa
                    logger.warning(f"Uszkodzony plik tymczasowy, usuwam")
                    temp_path.unlink()
                    resume_from = 0

        # Sprawdź połączenie sieciowe
        self.check_network()

        # Sprawdź miejsce na dysku
        if expected_size:
            self.check_disk_space(expected_size)

        # Pobieranie z retry
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Pobieranie {name} (próba {attempt}/{MAX_RETRIES})..."
                )

                # Przygotuj request z Range header jeśli resume
                req = Request(url)
                if resume_from > 0:
                    req.add_header("Range", f"bytes={resume_from}-")
                    logger.info(f"Wznawianie pobierania od bajtu {resume_from}")

                # Pobierz plik
                with urlopen(req, timeout=CHUNK_TIMEOUT) as response:
                    # Sprawdź kod odpowiedzi
                    if response.status == 416:  # Range Not Satisfiable
                        # Plik już kompletny, usuń .tmp i sprawdź
                        if temp_path.exists():
                            temp_path.unlink()
                        resume_from = 0
                        continue

                    # Otwórz plik w trybie append jeśli resume
                    mode = "ab" if resume_from > 0 else "wb"
                    with open(temp_path, mode) as f:
                        total_size = (
                            int(response.headers.get("Content-Length", 0))
                            + resume_from
                        )
                        downloaded = resume_from

                        # Pobierz w chunkach
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break

                            f.write(chunk)
                            downloaded += len(chunk)

                            # Progress callback
                            if self.progress_callback and total_size > 0:
                                progress = downloaded / total_size
                                self.progress_callback(name, progress)

                # Przenieś do docelowej lokalizacji
                temp_path.rename(dest)
                dest.chmod(0o755)

                # Weryfikuj checksum jeśli dostępny
                if expected_checksum:
                    if not self.verify_checksum(dest, expected_checksum):
                        logger.error(f"Błędny checksum dla {name}")
                        dest.unlink()
                        raise ChecksumError(
                            f"Checksum nie zgadza się dla {name}"
                        )

                logger.info(f"✓ Pobrano {name}")
                return

            except HTTPError as e:
                if e.code >= 500 and attempt < MAX_RETRIES:
                    # Serwer niedostępny, retry z backoff
                    wait_time = 2 ** (attempt - 1)
                    logger.warning(
                        f"Serwer niedostępny ({e.code}), "
                        f"retry za {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                raise DownloadError(f"Błąd HTTP {e.code}: {e.reason}")

            except URLError as e:
                if attempt < MAX_RETRIES:
                    wait_time = 2 ** (attempt - 1)
                    logger.warning(
                        f"Błąd połączenia, retry za {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                raise NetworkError(f"Błąd połączenia: {e.reason}")

            except (TimeoutError, socket.timeout):
                if attempt < MAX_RETRIES:
                    logger.warning(f"Timeout, retry {attempt + 1}/{MAX_RETRIES}")
                    continue
                raise DownloadError(f"Timeout podczas pobierania {name}")

            except Exception as e:
                logger.error(f"Nieoczekiwany błąd podczas pobierania {name}: {e}")
                if attempt < MAX_RETRIES:
                    continue
                raise DownloadError(f"Błąd podczas pobierania {name}: {e}")

        raise DownloadError(
            f"Nie udało się pobrać {name} po {MAX_RETRIES} próbach"
        )

    def download_whisper(self) -> bool:
        """Pobierz whisper.cpp binary.

        Returns:
            True jeśli pobieranie się powiodło

        Raises:
            RuntimeError: Jeśli architektura nie jest ARM64
            DownloadError: Jeśli pobieranie się nie powiodło
        """
        arch = platform.machine()
        if arch != "arm64":
            raise RuntimeError(f"Nieobsługiwana architektura: {arch}")

        url = URLS["whisper"]
        dest = self.bin_dir / "whisper-cli"
        expected_size = SIZES.get("whisper-cli")
        expected_checksum = CHECKSUMS.get("whisper-cli")

        if self.is_whisper_installed():
            logger.info("whisper-cli już zainstalowany")
            return True

        self._download_file(url, dest, "whisper-cli", expected_size, expected_checksum)
        return True

    def download_ffmpeg(self) -> bool:
        """Pobierz ffmpeg binary.

        Returns:
            True jeśli pobieranie się powiodło

        Raises:
            RuntimeError: Jeśli architektura nie jest ARM64
            DownloadError: Jeśli pobieranie się nie powiodło
        """
        arch = platform.machine()
        if arch != "arm64":
            raise RuntimeError(f"Nieobsługiwana architektura: {arch}")

        url = URLS["ffmpeg"]
        dest = self.bin_dir / "ffmpeg"
        expected_size = SIZES.get("ffmpeg-arm64")
        expected_checksum = CHECKSUMS.get("ffmpeg-arm64")

        if self.is_ffmpeg_installed():
            logger.info("ffmpeg już zainstalowany")
            return True

        self._download_file(url, dest, "ffmpeg", expected_size, expected_checksum)
        return True

    def download_model(self, model: str = "small") -> bool:
        """Pobierz model whisper.

        Args:
            model: Nazwa modelu (default: "small")

        Returns:
            True jeśli pobieranie się powiodło

        Raises:
            ValueError: Jeśli nieznany model
            DownloadError: Jeśli pobieranie się nie powiodło
        """
        url = URLS.get(f"model_{model}")
        if not url:
            raise ValueError(f"Nieznany model: {model}")

        dest = self.models_dir / f"ggml-{model}.bin"
        expected_size = SIZES.get(f"ggml-{model}.bin")
        expected_checksum = CHECKSUMS.get(f"ggml-{model}.bin")

        if self.is_model_installed(model):
            logger.info(f"Model {model} już zainstalowany")
            return True

        self._download_file(
            url, dest, f"model-{model}", expected_size, expected_checksum
        )
        return True

    def download_all(self) -> bool:
        """Pobierz wszystkie brakujące zależności.

        Returns:
            True jeśli wszystkie zależności zostały pobrane

        Raises:
            DownloadError: Jeśli pobieranie się nie powiodło
        """
        try:
            # Sprawdź połączenie sieciowe
            self.check_network()

            # Sprawdź miejsce na dysku (suma wszystkich plików)
            total_size = sum(SIZES.values())
            self.check_disk_space(total_size)

            # Pobierz brakujące zależności
            if not self.is_whisper_installed():
                self.download_whisper()

            if not self.is_ffmpeg_installed():
                self.download_ffmpeg()

            if not self.is_model_installed():
                self.download_model()

            logger.info("✓ Wszystkie zależności zainstalowane")
            return True

        except (NetworkError, DiskSpaceError, DownloadError) as e:
            logger.error(f"Błąd podczas pobierania zależności: {e}")
            raise

