# Testing whisper.cpp Integration

This document outlines how to test the whisper.cpp integration with Core ML support.

## Prerequisites

Before testing, ensure you've completed:

1. ✅ Updated configuration (config.py)
2. ✅ Created installation script (scripts/install_whisper_cpp.sh)
3. ✅ Updated transcriber logic
4. ✅ Updated documentation

## Installation Test

### Step 1: Install whisper.cpp

```bash
cd ~/CODE/Olympus_transcription
bash scripts/install_whisper_cpp.sh
```

**Expected outcome:**
- whisper.cpp cloned to `~/whisper.cpp`
- Compiled with Core ML support (on Apple Silicon)
- Model `ggml-small.bin` downloaded
- Core ML model generated (if applicable)

**Verify:**
```bash
# Check binary exists
ls -lh ~/whisper.cpp/main

# Check model exists
ls -lh ~/whisper.cpp/models/ggml-small.bin

# Check Core ML model (Apple Silicon only)
ls -d ~/whisper.cpp/models/ggml-small-encoder.mlmodelc

# Test whisper.cpp
~/whisper.cpp/main -h
```

### Step 2: Test Application Startup

```bash
cd ~/CODE/Olympus_transcription
source venv/bin/activate
python src/main.py
```

**Expected logs:**
```
🚀 Olympus Transcriber starting...
✓ Found whisper.cpp at: /Users/username/whisper.cpp/main
✓ Found ffmpeg at: /opt/homebrew/bin/ffmpeg
✓ Core ML model found - GPU acceleration enabled  # Apple Silicon only
✓ FSEvents monitor started
✓ Periodic checker started
✓ All monitors running
⏳ Waiting for recorder connection...
```

**Verify:**
- No "whisper.cpp not found" errors
- No "openai-whisper" or "MPS" references in logs
- Core ML detection working (if on Apple Silicon)

## Transcription Test

### Step 3: Test with Sample Audio

Create or use a sample audio file:

```bash
# Option 1: Use existing recording
# Connect your Olympus recorder with a recording

# Option 2: Create test file (requires sox)
brew install sox
sox -n -r 16000 -c 1 test.wav synth 5 sine 440
```

### Step 4: Manual Transcription Test

```bash
# Test whisper.cpp directly
~/whisper.cpp/main \
  -m ~/whisper.cpp/models/ggml-small.bin \
  -f test.wav \
  -l pl \
  -otxt \
  -of test_output

# Check output
cat test_output.txt
```

**Expected outcome:**
- Transcription completes without errors
- Output file created
- On Apple Silicon: check if Core ML was used (faster processing)

### Step 5: Application Transcription Test

With application running and recorder connected:

```bash
# Watch logs in another terminal
tail -f ~/Library/Logs/olympus_transcriber.log
```

**Expected logs (Core ML path + post-processing):**
```
📢 Detected recorder activity: /Volumes/LS-P1
✓ Recorder detected: /Volumes/LS-P1
📁 Found 1 new audio file(s)
🎙️  Starting transcription: 251118_0058.MP3
🔄 Attempting transcription with Core ML acceleration
🧠  Summarization enabled - provider: claude (haiku)
📝  Writing Markdown: /.../11-Transcripts/2025-11-20_Test.md
✓ whisper.cpp process completed, verifying output file...
✓ Transcription complete: 251118_0058.MP3
  Output: /path/to/output/2025-11-20_Test.md
```

**Verify:**
- No MPS-related errors
- No fallback to openai-whisper
- Transcription completes successfully
- Markdown file (not TXT) created with YAML frontmatter + summary/title

### Step 5b: Summarization ON (LLM path)

1. Ensure env / config:
   ```bash
   export ANTHROPIC_API_KEY=sk-...
   export ENABLE_SUMMARIZATION=true
   ```
2. Run Step 5 again with a fresh recording.

**Additional logs to expect:**
```
🧠  Generating summary via Claude (claude-3-haiku-20240307)...
📝  Markdown saved: .../YYYY-MM-DD_Title.md
```

**Checks:**
- Markdown file contains YAML frontmatter (`title`, `date`, `duration`, `summary`, `tags`).
- Title derived from summary, filename `YYYY-MM-DD_Title.md`.
- If API fails you should see: `⚠️  Summarization failed (Claude): <reason> – using fallback title`, but transcription must still finish.

### Step 5c: Summarization OFF (fallback to filename)

1. Disable summarization temporarily:
   ```bash
   export ENABLE_SUMMARIZATION=false
   python src/main.py
   ```
2. Trigger a transcription.

**Logs to expect:**
```
⚙️  Summarization disabled in config – using filename-based title
📝  Writing Markdown: .../YYYY-MM-DD_recording-name.md
```

**Checks:**
- Markdown still produced but title equals sanitized filename.
- No outbound LLM calls.
- After test, restore `ENABLE_SUMMARIZATION=true` (or unset env) for normal operation.

## Performance Test

### Step 6: Measure Speed Improvement

Test with a recording of known duration (e.g., 5 minutes):

**Before (medium model, CPU):**
- Expected time: ~20-25 minutes

**After (small model, Core ML):**
- Expected time on Apple Silicon: ~2-5 minutes (4-10x faster)
- Expected time on Intel CPU: ~8-12 minutes (2-3x faster due to smaller model)

**Verify:**
```bash
# Check transcription time in logs
grep "Starting transcription" ~/Library/Logs/olympus_transcriber.log
grep "Transcription complete" ~/Library/Logs/olympus_transcriber.log
# Optional: capture markdown pipeline timing
grep -E "🧠|📝" ~/Library/Logs/olympus_transcriber.log
```

## Core ML Fallback Test

### Step 7: Test CPU Fallback

Force disable Core ML to test fallback:

```bash
# Edit config temporarily
# In src/config.py, add: WHISPER_DEVICE = "cpu"

# Or set environment variable
WHISPER_COREML=0 python src/main.py
```

**Expected logs:**
```
🔄 Attempting transcription with Core ML acceleration
⚠️  Core ML failed, falling back to CPU for recording.mp3
🔄 Retrying transcription with CPU only
✓ Transcription complete: recording.mp3
⚠️  Summarization skipped (transcription fallback mode) – using filename title
```

**Verify:**
- Fallback works smoothly
- Transcription still completes
- No crashes or errors
- Markdown still produced (may use fallback title / no summary)

## Quality Test

### Step 8: Verify Transcription Quality

Compare transcription quality between models:

**Test files:**
- Polish speech sample
- English speech sample (if applicable)
- Recording with background noise

**Verify:**
- Small model quality is acceptable for your use case
- Polish language correctly detected
- Output format matches expectations

## Integration Test

### Step 9: End-to-End Test

Complete workflow test:

1. Stop application: `Ctrl+C`
2. Install as daemon: `./setup.sh`
3. Connect recorder with new recordings
4. Wait for automatic processing
5. Check output in Obsidian vault

**Verify:**
```bash
# Check daemon status
launchctl list | grep olympus-transcriber

# Check logs
tail -f ~/Library/Logs/olympus_transcriber.log

# Check output directory
ls -lh "/Users/username/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/11-Transcripts/"
```

## Cleanup Test

### Step 10: Verify No Leftover Dependencies

```bash
# Check that openai-whisper is not imported
cd ~/CODE/Olympus_transcription
source venv/bin/activate
python -c "import sys; 'whisper' in sys.modules and print('ERROR: whisper module found')"

# Should not print anything

# Verify no PyTorch dependency
pip list | grep -i torch
# Should show nothing or only minimal torch dependencies
```

## Success Criteria

✅ All tests pass if:
1. whisper.cpp installs successfully
2. Application starts without errors
3. Transcription completes successfully
4. Core ML acceleration works (Apple Silicon)
5. CPU fallback works when needed
6. Performance improved 3-10x depending on hardware
7. Output quality acceptable
8. End-to-end workflow functions correctly
9. No old dependencies remain

## Troubleshooting

### whisper.cpp compilation fails
- Check Xcode Command Line Tools: `xcode-select --install`
- Check for compilation errors in installation script output
- Try manual compilation: `cd ~/whisper.cpp && make clean && make`

### Core ML model not found
- Normal on Intel Macs (Core ML is Apple Silicon only)
- On M1/M2/M3: Re-run `bash scripts/install_whisper_cpp.sh`
- Check Python dependencies: `pip install ane_transformers coremltools`

### Transcription fails
- Check ffmpeg: `which ffmpeg`
- Check whisper.cpp: `~/whisper.cpp/main -h`
- Check model file: `ls ~/whisper.cpp/models/ggml-small.bin`
- Check logs for detailed error messages

### Slow performance
- Verify Core ML model exists (Apple Silicon)
- Check CPU usage during transcription
- Try smaller model: change `WHISPER_MODEL = "base"` or `"tiny"`

## Report Results

After testing, document:
- Hardware: Mac model, chip (M1/M2/M3/Intel)
- Installation time: How long whisper.cpp setup took
- Transcription speed: Time for 5-minute recording
- Quality assessment: Is small model acceptable?
- Issues encountered: Any problems during testing

Save results to help with future debugging and optimization.

