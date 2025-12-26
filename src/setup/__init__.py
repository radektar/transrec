"""Setup module for Transrec - dependency downloading and installation."""

from src.setup.downloader import DependencyDownloader
from src.setup.errors import (
    DownloadError,
    ChecksumError,
    NetworkError,
    DiskSpaceError,
)

__all__ = [
    "DependencyDownloader",
    "DownloadError",
    "ChecksumError",
    "NetworkError",
    "DiskSpaceError",
]

