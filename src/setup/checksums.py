"""Checksums, URLs, and versions for dependencies."""

# Wersje zależności
VERSIONS = {
    "whisper": "1.0.0",
    "ffmpeg": "6.1",
    "model_small": "latest",
}

# SHA256 checksums (zostaną zaktualizowane po utworzeniu GitHub Release)
CHECKSUMS = {
    "whisper-cli-arm64": "",  # TODO: Zaktualizować po build
    "ffmpeg-arm64": "",  # TODO: Zaktualizować po build
    "ggml-small.bin": "",  # TODO: Zaktualizować po pobraniu z HuggingFace
}

# URLs dla pobierania
# TODO: Zaktualizować po utworzeniu repo transrec-deps
URLS = {
    "whisper": "https://github.com/USER/transrec-deps/releases/download/v1.0/whisper-cli-arm64",
    "ffmpeg": "https://github.com/USER/transrec-deps/releases/download/v1.0/ffmpeg-arm64",
    "model_small": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
}

# Oczekiwane rozmiary plików (w bajtach)
SIZES = {
    "whisper-cli-arm64": 10_000_000,  # ~10MB
    "ffmpeg-arm64": 15_000_000,  # ~15MB
    "ggml-small.bin": 466_000_000,  # ~466MB
}

