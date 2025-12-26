"""Checksums, URLs, and versions for dependencies."""

# Wersje zależności
VERSIONS = {
    "whisper": "1.0.0",
    "ffmpeg": "6.1",
    "model_small": "latest",
}

# SHA256 checksums (verified from deps-v1.0.0 release)
CHECKSUMS = {
    "whisper-cli": "32a13ba35401b174a3096d67880e2cf11edbbb611891b0fb7844afc750504451",
    "ffmpeg-arm64": "430d60fbf419dab28daee9b679e7929a31ee9bae53f6e42e8ae26b725584290f",
    "ggml-small.bin": "1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b",
}

# URLs dla pobierania
URLS = {
    "whisper": "https://github.com/radektar/transrec/releases/download/deps-v1.0.0/whisper-cli",
    "ffmpeg": "https://github.com/radektar/transrec/releases/download/deps-v1.0.0/ffmpeg-arm64",
    "model_small": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
}

# Oczekiwane rozmiary plików (w bajtach) - verified from release
SIZES = {
    "whisper-cli": 824_360,  # ~800KB
    "ffmpeg-arm64": 80_083_328,  # ~76MB
    "ggml-small.bin": 487_601_967,  # ~465MB
}

