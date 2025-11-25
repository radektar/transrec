"""Utility script to deduplicate Obsidian transcripts in 11-Transcripts.

This script groups markdown notes by their ``source: <AUDIO_FILE>`` field in
YAML frontmatter and moves lower-quality duplicates to a ``_duplicates``
subdirectory. The goal is:

- keep the best-quality note(s) for each recording
- remove clutter from the main `11-Transcripts` folder without deleting data

Heuristics:
- If there are filenames starting with ``YY-MM-DD - ...`` (two-digit year),
  they are treated as the newer, higher-quality template and are kept.
- Older files with four-digit year prefixes (``YYYY-MM-DD_...``) are treated
  as duplicates and moved to ``_duplicates``.
- If only four-digit-style files exist for a given ``source`` and there are
  multiple, the largest file by size is kept and the rest are moved.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from src.config import config
from src.logger import logger


@dataclass
class NoteInfo:
    """Metadata about a single transcript note."""

    path: Path
    size: int


def _find_source_for_note(note_path: Path) -> Optional[str]:
    """Extract the ``source:`` value from a markdown note.

    Args:
        note_path: Path to markdown file.

    Returns:
        The raw ``source`` value (e.g. ``250819_0037.MP3``) or None if
        not found or the file could not be read.
    """
    try:
        with note_path.open("r", encoding="utf-8") as handle:
            for _ in range(30):
                line = handle.readline()
                if not line:
                    break
                if line.startswith("source: "):
                    return line.strip().split("source: ", maxsplit=1)[1]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read note %s: %s", note_path, exc)
    return None


def _is_twodigit_filename(note_path: Path) -> bool:
    """Check if filename uses the ``YY-MM-DD - Title.md`` pattern.

    This corresponds to the newer markdown generator naming convention and
    is treated as the preferred variant when cleaning duplicates.

    Args:
        note_path: Path to markdown file.

    Returns:
        True if filename looks like ``YY-MM-DD - ...``, False otherwise.
    """
    name = note_path.name
    if len(name) < 9:
        return False

    prefix = name[:8]
    if not (
        prefix[0:2].isdigit()
        and prefix[2] == "-"
        and prefix[3:5].isdigit()
        and prefix[5] == "-"
        and prefix[6:8].isdigit()
    ):
        return False

    # Also require a separating " - " afterwards for extra safety
    return name[8:11] == " - "


def cleanup_transcripts(transcribe_dir: Path) -> None:
    """Deduplicate markdown notes in the given transcription directory.

    Args:
        transcribe_dir: Directory containing Obsidian markdown transcripts.
    """
    logger.info("Starting transcript cleanup in: %s", transcribe_dir)

    if not transcribe_dir.exists():
        logger.error("Transcription directory does not exist: %s", transcribe_dir)
        return

    groups: Dict[str, List[NoteInfo]] = {}

    for md_path in transcribe_dir.glob("*.md"):
        source = _find_source_for_note(md_path)
        if not source:
            # Legacy or non-standard note – leave untouched
            continue

        try:
            size = md_path.stat().st_size
        except OSError as exc:
            logger.warning("Could not stat %s: %s", md_path, exc)
            continue

        groups.setdefault(source, []).append(NoteInfo(path=md_path, size=size))

    duplicates_dir = transcribe_dir / "_duplicates"
    duplicates_dir.mkdir(parents=True, exist_ok=True)

    total_moved = 0
    total_groups = 0

    for source, notes in groups.items():
        if len(notes) <= 1:
            continue

        total_groups += 1

        twodigit_notes: List[NoteInfo] = [
            note for note in notes if _is_twodigit_filename(note.path)
        ]

        keep_paths: Set[Path]
        to_move: List[NoteInfo]

        if twodigit_notes:
            # Prefer newer two-digit filenames; move all others.
            keep_paths = {note.path for note in twodigit_notes}
            to_move = [note for note in notes if note.path not in keep_paths]
        else:
            # Only legacy four-digit-style filenames exist; keep the largest.
            sorted_notes = sorted(notes, key=lambda n: n.size, reverse=True)
            keep_paths = {sorted_notes[0].path}
            to_move = sorted_notes[1:]

        if not to_move:
            continue

        logger.info(
            "Source %s: keeping %d note(s), moving %d duplicate(s)",
            source,
            len(keep_paths),
            len(to_move),
        )

        for note in to_move:
            target = duplicates_dir / note.path.name
            try:
                note.path.rename(target)
                total_moved += 1
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to move %s -> %s: %s", note.path, target, exc)

    logger.info(
        "Transcript cleanup complete: %d duplicate file(s) moved from %d group(s) "
        "into %s",
        total_moved,
        total_groups,
        duplicates_dir,
    )


if __name__ == "__main__":
    cleanup_transcripts(config.TRANSCRIBE_DIR)


