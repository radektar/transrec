"""Transcription engine for Olympus Transcriber."""

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.config import config
from src.logger import logger
from src.summarizer import get_summarizer, BaseSummarizer
from src.markdown_generator import MarkdownGenerator
from src.app_status import AppStatus
from src.state_manager import get_last_sync_time, save_sync_time
from src.tag_index import TagIndex
from src.tagger import BaseTagger, get_tagger


def send_notification(title: str, message: str, subtitle: str = "") -> None:
    """Send macOS notification using osascript.
    
    Args:
        title: Notification title
        message: Notification message body
        subtitle: Optional subtitle
    """
    try:
        # Escape quotes in strings
        title = title.replace('"', '\\"')
        message = message.replace('"', '\\"')
        subtitle = subtitle.replace('"', '\\"')
        
        if subtitle:
            script = f'display notification "{message}" with title "{title}" subtitle "{subtitle}"'
        else:
            script = f'display notification "{message}" with title "{title}"'
        
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5.0,
            check=False
        )
    except Exception as e:
        logger.debug(f"Failed to send notification: {e}")


class ProcessLock:
    """File-based lock guarding recorder workflow execution."""

    def __init__(self, lock_path: Path):
        """Configure lock helper.

        Args:
            lock_path: Full path to lock file.
        """
        self.lock_path = lock_path
        self._fd: Optional[int] = None

    def acquire(self) -> bool:
        """Attempt to acquire the lock.

        Returns:
            True if lock acquired, False otherwise.
        """
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            self._fd = os.open(
                str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
            os.write(self._fd, f"{time.time():.0f}".encode("utf-8"))
            return True
        except FileExistsError:
            return False
        except OSError as error:
            logger.error("Could not create process lock at %s: %s", self.lock_path, error)
            return False

    def release(self) -> None:
        """Release the lock if held."""
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError as error:
                logger.warning("Error closing process lock descriptor: %s", error)
            finally:
                self._fd = None
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except OSError as error:
            logger.warning("Could not remove process lock file %s: %s", self.lock_path, error)

class Transcriber:
    """Main transcription engine.
    
    Handles finding the recorder, scanning for new audio files,
    managing transcription state, and invoking Whisper CLI.
    
    Attributes:
        transcription_in_progress: Track files currently being transcribed
        whisper_available: Flag indicating if Whisper CLI is available
        recorder_monitoring: Flag if recorder is currently connected
        recorder_was_notified: Flag to track if connection notification was sent
        state_updater: Optional callback to update application state
    """
    
    def __init__(self):
        """Initialize the transcriber."""
        self.transcription_in_progress: Dict[str, bool] = {}
        self.whisper_available = self._check_whisper()
        self.recorder_monitoring = False
        self.recorder_was_notified = False
        self.state_updater: Optional[Callable[[AppStatus, Optional[str], Optional[str]], None]] = None
        
        # Initialize summarizer and markdown generator
        self.summarizer: Optional[BaseSummarizer] = get_summarizer()
        self.markdown_generator = MarkdownGenerator()
        self.tag_index = TagIndex()
        self.tagger: Optional[BaseTagger] = get_tagger()
        
        # Ensure output directory exists
        config.ensure_directories()
    
    def set_state_updater(
        self,
        updater: Callable[[AppStatus, Optional[str], Optional[str]], None]
    ) -> None:
        """Set callback function for state updates.
        
        Args:
            updater: Function that takes (status, current_file, error_message)
        """
        self.state_updater = updater
    
    def _update_state(
        self,
        status: AppStatus,
        current_file: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update application state via callback if available.
        
        Args:
            status: New status
            current_file: Current file being processed
            error_message: Error message if status is ERROR
        """
        if self.state_updater:
            try:
                self.state_updater(status, current_file, error_message)
            except Exception as e:
                logger.debug(f"Error updating state: {e}")
    
    def _check_whisper(self) -> bool:
        """Check if whisper.cpp binary and ffmpeg are available.
        
        Returns:
            True if both whisper.cpp and ffmpeg are available, False otherwise
        """
        # Check for whisper.cpp binary
        if not config.WHISPER_CPP_PATH.exists():
            logger.error(
                f"⚠️  whisper.cpp not found at: {config.WHISPER_CPP_PATH}\n"
                "Please run: bash scripts/install_whisper_cpp.sh"
            )
            return False
        
        # Check for ffmpeg
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            logger.error(
                "⚠️  ffmpeg not found. whisper.cpp requires ffmpeg to process audio. "
                "Please install: brew install ffmpeg"
            )
            return False
        
        logger.info(f"✓ Found whisper.cpp at: {config.WHISPER_CPP_PATH}")
        logger.info(f"✓ Found ffmpeg at: {ffmpeg_path}")
        
        # Check for Core ML model (Apple Silicon optimization)
        coreml_model = (
            config.WHISPER_CPP_MODELS_DIR / 
            f"ggml-{config.WHISPER_MODEL}-encoder.mlmodelc"
        )
        if coreml_model.exists():
            logger.info("✓ Core ML model found - GPU acceleration enabled")
        else:
            logger.info("ℹ️  Core ML model not found - using CPU (still fast)")
        
        return True
    
    def find_recorder(self) -> Optional[Path]:
        """Search for connected Olympus recorder.
        
        Returns:
            Path to recorder volume or None if not found
        """
        volumes_path = Path("/Volumes")
        
        if not volumes_path.exists():
            logger.debug("/Volumes directory not found")
            return None
        
        # Check each possible recorder name
        for name in config.RECORDER_NAMES:
            recorder = volumes_path / name
            if recorder.exists() and recorder.is_dir():
                logger.info(f"✓ Recorder found: {recorder}")
                return recorder
        
        logger.debug("No recorder found in /Volumes")
        return None
    
    def get_last_sync_time(self) -> datetime:
        """Get timestamp of last synchronization.
        
        Returns:
            Datetime of last sync, or 7 days ago if no state file exists
        """
        return get_last_sync_time()
    
    def save_sync_time(self) -> None:
        """Save current time as last sync timestamp."""
        save_sync_time()
    
    def find_audio_files(
        self, recorder_path: Path, since: datetime
    ) -> List[Path]:
        """Find new audio files modified after given datetime.
        
        Args:
            recorder_path: Root path of the recorder volume
            since: Only return files modified after this datetime
            
        Returns:
            List of audio file paths, sorted by modification time
        """
        new_files = []
        
        try:
            # Recursively find all files
            for item in recorder_path.rglob("*"):
                # Skip directories and non-audio files
                if not item.is_file():
                    continue
                
                # Skip macOS metadata files
                if item.name.startswith('._') or item.name == '.DS_Store':
                    logger.debug(f"Skipping macOS metadata file: {item.name}")
                    continue
                
                if item.suffix.lower() not in config.AUDIO_EXTENSIONS:
                    continue
                
                # Check modification time
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime > since:
                        new_files.append(item)
                        logger.debug(f"Found new file: {item.name} (mtime: {mtime})")
                except OSError as e:
                    logger.warning(f"Could not access file {item}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scanning for audio files: {e}")
            return []
        
        # Sort by modification time (oldest first)
        new_files.sort(key=lambda x: x.stat().st_mtime)
        
        return new_files
    
    def _stage_audio_file(self, audio_file: Path) -> Optional[Path]:
        """Copy audio file from recorder to local staging directory.
        
        Creates a local copy of the recorder file in the staging directory.
        This allows transcription to proceed even if the recorder unmounts
        during processing. The staged file preserves the original filename
        and modification time.
        
        Args:
            audio_file: Path to audio file on recorder (e.g., /Volumes/LS-P1/...)
            
        Returns:
            Path to staged file in LOCAL_RECORDINGS_DIR, or None if staging failed
        """
        try:
            # Ensure staging directory exists
            config.LOCAL_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
            
            # Destination path (same filename as original)
            staged_path = config.LOCAL_RECORDINGS_DIR / audio_file.name
            
            # Check if file already exists and matches (size and mtime)
            if staged_path.exists():
                try:
                    source_stat = audio_file.stat()
                    staged_stat = staged_path.stat()
                    
                    # If size and mtime match, reuse existing copy
                    if (source_stat.st_size == staged_stat.st_size and
                        abs(source_stat.st_mtime - staged_stat.st_mtime) < 1.0):
                        logger.debug(
                            f"✓ Reusing existing staged copy: {audio_file.name}"
                        )
                        return staged_path
                except OSError:
                    # If we can't stat the source, try to copy anyway
                    # (might be a race condition with unmounting)
                    pass
            
            # Copy file with metadata preservation
            logger.debug(f"📋 Staging file: {audio_file.name}")
            shutil.copy2(audio_file, staged_path)
            logger.debug(f"✓ Staged: {audio_file.name} -> {staged_path}")
            
            return staged_path
            
        except FileNotFoundError as e:
            logger.warning(
                f"⚠️  Could not stage {audio_file.name}: "
                f"recorder may have unmounted ({e})"
            )
            return None
        except OSError as e:
            logger.warning(
                f"⚠️  Could not stage {audio_file.name}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"✗ Unexpected error staging {audio_file.name}: {e}",
                exc_info=True
            )
            return None
    
    def _run_whisper_transcription(
        self, audio_file: Path, use_coreml: bool = True
    ) -> subprocess.CompletedProcess:
        """Run whisper.cpp transcription.
        
        Args:
            audio_file: Path to the audio file to transcribe
            use_coreml: Whether to allow Core ML acceleration (disable for fallback)
            
        Returns:
            CompletedProcess from subprocess.run
        """
        # Build whisper.cpp command
        model_path = config.WHISPER_CPP_MODELS_DIR / f"ggml-{config.WHISPER_MODEL}.bin"
        output_base = config.TRANSCRIBE_DIR / audio_file.stem
        
        whisper_cmd = [
            str(config.WHISPER_CPP_PATH),
            "-m", str(model_path),
            "-f", str(audio_file),
            "-otxt",
            "-of", str(output_base),
        ]
        
        # Add language if specified
        if config.WHISPER_LANGUAGE:
            whisper_cmd.extend(["-l", config.WHISPER_LANGUAGE])
        
        # Set environment for Core ML control
        env = None
        if not use_coreml:
            env = {**subprocess.os.environ, "WHISPER_COREML": "0"}
            logger.debug("Core ML disabled for this attempt")
        
        logger.debug(
            f"Running whisper.cpp: model={config.WHISPER_MODEL}, "
            f"language={config.WHISPER_LANGUAGE}, "
            f"coreml={'enabled' if use_coreml else 'disabled'}, "
            f"timeout={config.TRANSCRIPTION_TIMEOUT}s"
        )
        
        return subprocess.run(
            whisper_cmd,
            capture_output=True,
            timeout=config.TRANSCRIPTION_TIMEOUT,
            text=True,
            env=env,
        )

    def _should_retry_without_coreml(
        self, stderr: Optional[str], use_coreml_attempted: bool
    ) -> bool:
        """Determine if whisper run should be retried without Core ML acceleration.

        Args:
            stderr: stderr output from whisper.cpp invocation.
            use_coreml_attempted: True if the failed run tried Core ML.

        Returns:
            True when stderr indicates Metal/Core ML failures and CPU retry is warranted.
        """
        if not use_coreml_attempted or not stderr:
            return False

        retry_markers = (
            "Core ML",
            "ggml_metal",
            "MTLLibrar",
            "tensor API disabled",
        )
        return any(marker in stderr for marker in retry_markers)
    
    def _run_macwhisper(self, audio_file: Path) -> Optional[Path]:
        """Run whisper.cpp transcription and return path to TXT file.
        
        Args:
            audio_file: Path to the audio file to transcribe
            
        Returns:
            Path to created TXT file, or None if transcription failed
        """
        if not self.whisper_available:
            logger.error("whisper.cpp not available, cannot transcribe")
            return None
        
        # Generate expected output file path
        output_file = config.TRANSCRIBE_DIR / f"{audio_file.stem}.txt"
        file_id = audio_file.stem
        
        # Check if already in progress
        if file_id in self.transcription_in_progress:
            logger.info(f"⏳ Already transcribing: {audio_file.name}")
            return None
        
        # Check if already transcribed (check for both TXT and MD)
        if output_file.exists():
            logger.info(f"✓ Already transcribed: {audio_file.name}")
            return output_file
        
        # Check if markdown version exists
        md_pattern = f"{audio_file.stem}*.md"
        existing_md = list(config.TRANSCRIBE_DIR.glob(md_pattern))
        if existing_md:
            logger.info(f"✓ Already transcribed (markdown exists): {audio_file.name}")
            return None
        
        logger.info(f"🎙️  Starting transcription: {audio_file.name}")
        self.transcription_in_progress[file_id] = True
        self._update_state(AppStatus.TRANSCRIBING, audio_file.name)
        
        try:
            # Ensure output directory exists
            config.TRANSCRIBE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Try with Core ML acceleration first (if available)
            logger.info("🔄 Attempting transcription with Core ML acceleration")
            result = self._run_whisper_transcription(audio_file, use_coreml=True)
            
            logger.debug(
                f"Transcription attempt completed - "
                f"returncode: {result.returncode}, "
                f"stderr length: {len(result.stderr) if result.stderr else 0}"
            )
            
            # If Core ML failed, retry without it
            if self._should_retry_without_coreml(result.stderr, use_coreml_attempted=True):
                logger.warning(
                    f"⚠️  Core ML/Metal failed, falling back to CPU for {audio_file.name}"
                )
                if result.stderr:
                    logger.debug(f"  Error details: {result.stderr[:500]}")

                logger.info("🔄 Retrying transcription with CPU only")
                result = self._run_whisper_transcription(audio_file, use_coreml=False)
                logger.debug(f"CPU retry completed - returncode: {result.returncode}")
            
            # Check for errors
            if result.returncode != 0:
                error_msg = f"Transkrypcja nieudana (kod: {result.returncode})"
                if result.stderr:
                    error_msg = result.stderr[:200]
                logger.error(f"✗ Transcription failed: {audio_file.name}")
                logger.error(f"  Return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"  Error: {result.stderr[:500]}")
                self._update_state(AppStatus.ERROR, audio_file.name, error_msg)
                return None
            
            logger.debug("✓ whisper.cpp process completed, verifying output file...")
            
            # Verify output file was created
            logger.debug(f"Checking for output file: {output_file}")
            if output_file.exists():
                logger.debug(f"✓ Transcription TXT created: {output_file}")
                return output_file
            else:
                logger.warning(
                    f"⚠️  Expected output file not found: {output_file}, "
                    f"searching for alternative files..."
                )
                # List what files were actually created
                output_dir = config.TRANSCRIBE_DIR
                created_files = list(output_dir.glob(f"{audio_file.stem}*"))
                logger.debug(
                    f"Found {len(created_files)} file(s) matching pattern "
                    f"'{audio_file.stem}*' in {output_dir}"
                )
                if created_files:
                    logger.warning(
                        f"⚠️  Expected output file not found, but found: "
                        f"{[f.name for f in created_files]}"
                    )
                    # Try to find .txt file with different name
                    txt_files = [f for f in created_files if f.suffix == ".txt"]
                    if txt_files:
                        logger.debug(f"✓ Using found file: {txt_files[0]}")
                        return txt_files[0]
                
                logger.error(
                    f"✗ Transcription completed but output file not found: "
                    f"{output_file}"
                )
                logger.error(f"  Searched directory: {output_dir}")
                logger.error(f"  Files found matching pattern: {len(created_files)}")
                if result.stderr:
                    logger.error(f"  stderr: {result.stderr}")
                if result.stdout:
                    logger.debug(f"  stdout: {result.stdout}")
                return None
        
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ({config.TRANSCRIPTION_TIMEOUT}s)"
            logger.error(
                f"✗ Transcription timeout ({config.TRANSCRIPTION_TIMEOUT}s): "
                f"{audio_file.name}"
            )
            self._update_state(AppStatus.ERROR, audio_file.name, error_msg)
            return None
        
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(
                f"✗ Error transcribing {audio_file.name}: {e}",
                exc_info=True
            )
            self._update_state(AppStatus.ERROR, audio_file.name, error_msg)
            return None
        
        finally:
            # Remove from in-progress tracking
            self.transcription_in_progress.pop(file_id, None)
            # Reset state if no more files in progress
            if not self.transcription_in_progress:
                self._update_state(AppStatus.IDLE)
    
    def _postprocess_transcript(
        self, audio_file: Path, transcript_path: Path
    ) -> bool:
        """Post-process transcript: generate summary and create markdown.
        
        Args:
            audio_file: Original audio file path
            transcript_path: Path to temporary TXT transcript file
            
        Returns:
            True if post-processing succeeded, False otherwise
        """
        try:
            # Read transcript
            logger.debug(f"Reading transcript from: {transcript_path}")
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()
            
            if not transcript_text.strip():
                logger.warning("Empty transcript, skipping post-processing")
                return False
            
            # Generate summary (if summarizer available)
            summary = None
            if self.summarizer:
                try:
                    logger.info("📝 Generating summary...")
                    summary = self.summarizer.generate(transcript_text)
                    logger.info(f"✓ Summary generated: {summary.get('title', 'N/A')}")
                except Exception as e:
                    logger.error(f"Summary generation failed: {e}", exc_info=True)
                    logger.warning("Continuing without summary")
                    summary = None
            
            # Fallback summary if summarizer unavailable
            if not summary:
                logger.debug("Using fallback summary")
                summary = {
                    "title": audio_file.stem.replace("_", " ").title(),
                    "summary": """## Podsumowanie

Brak podsumowania. Podsumowanie można wygenerować po skonfigurowaniu API Claude (ANTHROPIC_API_KEY).

## Lista działań (To-do)

- Przejrzeć transkrypcję ręcznie
- Wyciągnąć kluczowe wnioski ze spotkania"""
                }
            
            # Extract audio metadata
            logger.debug("Extracting audio metadata...")
            metadata = self.markdown_generator.extract_audio_metadata(audio_file)

            # Generate tags
            tags = ["transcription"]
            if config.ENABLE_LLM_TAGGING and self.tagger:
                try:
                    existing_tags = self.tag_index.existing_tags()
                    generated_tags = self.tagger.generate_tags(
                        transcript=transcript_text,
                        summary_markdown=summary.get("summary", ""),
                        existing_tags=existing_tags,
                    )
                    for tag in generated_tags:
                        if tag not in tags:
                            tags.append(tag)
                except Exception as error:  # noqa: BLE001
                    logger.error(
                        "Tag generation failed for %s: %s",
                        audio_file.name,
                        error,
                        exc_info=True,
                    )
            
            # Create markdown document
            logger.info("📄 Creating markdown document...")
            md_path = self.markdown_generator.create_markdown_document(
                transcript=transcript_text,
                summary=summary,
                metadata=metadata,
                output_dir=config.TRANSCRIBE_DIR,
                tags=tags
            )
            
            logger.info(f"✓ Markdown document created: {md_path.name}")
            
            # Delete temporary TXT file if configured
            if config.DELETE_TEMP_TXT:
                try:
                    transcript_path.unlink()
                    logger.debug(f"✓ Deleted temporary TXT file: {transcript_path.name}")
                except OSError as e:
                    logger.warning(f"Could not delete temporary TXT file: {e}")
            
            return True
            
        except Exception as e:
            logger.error(
                f"Post-processing failed for {audio_file.name}: {e}",
                exc_info=True
            )
            return False

    def _find_existing_markdown_for_audio(
        self, audio_file: Path
    ) -> Optional[Path]:
        """Find existing markdown note for given audio file.

        Looks for markdown files in the transcription directory whose YAML
        frontmatter contains a ``source: <audio_file.name>`` line. This allows
        us to reliably detect previously processed recordings even if markdown
        filenames change when the summary title changes.

        Args:
            audio_file: Audio file whose markdown note we want to find.

        Returns:
            Path to existing markdown file if found, otherwise None.
        """
        try:
            if not config.TRANSCRIBE_DIR.exists():
                return None

            for md_path in config.TRANSCRIBE_DIR.glob("*.md"):
                try:
                    with md_path.open("r", encoding="utf-8") as md_file:
                        # Read only the first few lines – frontmatter is at top
                        lines: List[str] = []
                        for _ in range(20):
                            line = md_file.readline()
                            if not line:
                                break
                            lines.append(line)

                        frontmatter = "".join(lines)
                        source_line = f"source: {audio_file.name}"
                        if source_line in frontmatter:
                            return md_path
                except OSError as read_error:
                    logger.warning(
                        "Could not read markdown file %s: %s",
                        md_path,
                        read_error,
                    )
                    continue
        except Exception as error:
            logger.error(
                "Error searching for existing markdown for %s: %s",
                audio_file.name,
                error,
            )

        return None
    
    def transcribe_file(self, audio_file: Path) -> bool:
        """Transcribe a single audio file using whisper.cpp.
        
        Automatically falls back to CPU-only if Core ML fails.
        Post-processes transcript to create markdown document with summary.
        
        Args:
            audio_file: Path to the audio file to transcribe
            
        Returns:
            True if transcription succeeded, False otherwise
        """
        # If markdown already exists for this audio (based on `source` field),
        # treat it as successfully transcribed and skip any further work.
        existing_md = self._find_existing_markdown_for_audio(audio_file)
        if existing_md:
            logger.info(
                "✓ Already transcribed (markdown exists for source): %s -> %s",
                audio_file.name,
                existing_md.name,
            )
            return True

        # If TXT transcript already exists, skip whisper and only post-process
        # once to create markdown. This avoids generating multiple notes for
        # the same recording while still allowing migration from raw TXT.
        transcript_path = (
            config.TRANSCRIBE_DIR / f"{audio_file.stem}.txt"
        )
        if transcript_path.exists():
            logger.info(
                "✓ Transcription TXT already exists, "
                "creating markdown if needed: %s",
                audio_file.name,
            )
            success = self._postprocess_transcript(audio_file, transcript_path)
            if success:
                logger.info("✓ Complete: %s", audio_file.name)
            else:
                logger.warning(
                    "⚠️  TXT exists but post-processing failed: %s",
                    audio_file.name,
                )
            return success

        # Run whisper transcription
        transcript_path = self._run_macwhisper(audio_file)
        
        if transcript_path is None:
            return False
        
        # Post-process: generate summary and create markdown
        success = self._postprocess_transcript(audio_file, transcript_path)
        
        if success:
            logger.info(f"✓ Complete: {audio_file.name}")
        else:
            logger.warning(f"⚠️  Transcription complete but post-processing failed: {audio_file.name}")
        
        return success
    
    def process_recorder(self) -> None:
        """Main workflow: detect recorder, find new files, transcribe.
        
        This is the main entry point called when recorder activity is detected.
        It orchestrates the entire transcription workflow.
        """
        lock = ProcessLock(config.PROCESS_LOCK_FILE)
        if not lock.acquire():
            logger.info(
                "⛔️ Skipping process_recorder because another instance holds lock %s",
                config.PROCESS_LOCK_FILE,
            )
            self._update_state(AppStatus.IDLE)
            return

        try:
            logger.info("=" * 60)
            logger.info("🔍 Checking for recorder...")
            self._update_state(AppStatus.SCANNING)
            
            # Find recorder
            recorder = self.find_recorder()
            if not recorder:
                logger.info("❌ Recorder not found")
                self.recorder_monitoring = False
                self.recorder_was_notified = False
                self._update_state(AppStatus.IDLE)
                return
            
            logger.info(f"✓ Recorder detected: {recorder}")
            
            # Send notification only if this is first detection (not periodic check)
            if not self.recorder_was_notified:
                send_notification(
                    title="Olympus Transcriber",
                    subtitle="Recorder wykryty",
                    message=f"Podłączono: {recorder.name}"
                )
                self.recorder_was_notified = True
            
            self.recorder_monitoring = True
            
            # Get last sync time
            last_sync = self.get_last_sync_time()
            logger.info(f"📅 Looking for files modified after: {last_sync}")
            
            # Find new audio files
            new_files = self.find_audio_files(recorder, last_sync)
            logger.info(f"📁 Found {len(new_files)} new audio file(s)")
            
            # Notify if new files found
            if new_files:
                send_notification(
                    title="Olympus Transcriber",
                    subtitle=f"Znaleziono {len(new_files)} nowych nagrań",
                    message="Rozpoczynam transkrypcję..."
                )
            
            processed_success = 0
            processed_failed = 0

            # Process each file: stage first, then transcribe
            if new_files:
                for recorder_file in new_files:
                    logger.info(f"Processing: {recorder_file.name}")
                    
                    existing_markdown = self._find_existing_markdown_for_audio(recorder_file)
                    if existing_markdown:
                        logger.info(
                            "↪️ Skipping already transcribed file: %s -> %s",
                            recorder_file.name,
                            existing_markdown.name,
                        )
                        processed_success += 1
                        continue
                    
                    # Stage file to local directory
                    staged_file = self._stage_audio_file(recorder_file)
                    if staged_file is None:
                        logger.warning(
                            f"⚠️  Failed to stage {recorder_file.name}, "
                            "skipping transcription"
                        )
                        processed_failed += 1
                        continue
                    
                    # Transcribe using staged file
                    if self.transcribe_file(staged_file):
                        processed_success += 1
                    else:
                        processed_failed += 1
                    
                    # Small delay between files
                    time.sleep(1)
                
                total_processed = processed_success + processed_failed
                logger.info(
                    f"✓ Transcription batch complete: "
                    f"{processed_success}/{total_processed} succeeded, "
                    f"{processed_failed}/{total_processed} failed"
                )
                
                # Send completion notification
                send_notification(
                    title="Olympus Transcriber",
                    subtitle="Transkrypcja zakończona",
                    message=f"Przetworzono: {processed_success}/{total_processed} plików"
                )
            else:
                logger.info("ℹ️  No new files to transcribe")
            
            # Only advance sync time if ALL files were successfully processed
            # This prevents losing files that failed due to unmounting or other errors
            if processed_failed == 0 and processed_success > 0:
                self.save_sync_time()
                logger.info("✓ Sync complete (state updated)")
            elif processed_failed > 0:
                logger.warning(
                    f"⚠️  Batch had {processed_failed} failure(s). "
                    "Not updating last_sync to avoid losing unprocessed files. "
                    "Failed files will be retried on next sync."
                )
            else:
                logger.info(
                    "ℹ️  Skipping sync update (no files processed). "
                    "State remains at previous value."
                )
            logger.info("=" * 60)
            
            # Keep recorder_monitoring True if recorder still connected
            # This prevents notification spam on periodic checks
            if not self.find_recorder():
                self.recorder_monitoring = False
                self.recorder_was_notified = False
            
            self._update_state(AppStatus.IDLE)
        finally:
            lock.release()

