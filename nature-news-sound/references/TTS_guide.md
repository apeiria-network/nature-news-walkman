# Nature News TTS Reference

This reference is for English TTS generation used by the `nature-news-sound` skill.

## TTS Guidelines

### Local Python Environment
- Audio generation for `nature-news-sound` uses the local Python runtime under `scripts/.venv`.
- If `scripts/.venv` does not exist yet, create it before generating audio.
- If the local runtime is missing required dependencies, install them into that same `scripts/.venv`.
- Reuse the same local runtime throughout the audio step, and avoid changing unrelated Python environments.
- Preferred Python range for this skill is **3.10-3.13**.
- The helper also allows **3.14** when available, but **3.10-3.13** is the more reliable range to use by default.

### Typical Setup Steps

```sh
# Create the local runtime under scripts/
python3 -m venv scripts/.venv

# Activate the local runtime
source scripts/.venv/bin/activate

# Install sound dependencies into the local runtime
pip install -r scripts/requirements.txt

# Run the script through the local runtime
python scripts/nature_news_digest.py --output-dir .claude/nature-news-walkman
```

Use these shell-style steps as a manual setup or troubleshooting reference. The runtime helper remains the main enforcement mechanism during normal TTS execution.

### Storage Directory
- The default project storage directory for generated audio and shortlist cache is `.claude/nature-news-walkman/` under the project root.
- Before saving shortlist cache, the workflow should tell the user which storage path will be used.
- If audio file delivery fails, tell the user the current saved file path under that directory so the file can be retrieved manually.

### Text Preparation for TTS
1. Remove markdown formatting (*, **, #, etc.)
2. Remove credit lines ("Credit: ...")
3. Remove image references
4. Expand abbreviations on first mention in spoken form
5. Clean up special characters that TTS engines may mispronounce

### TTS Engine Selection

| Engine | Priority | Network | Quality | Notes |
|--------|----------|---------|---------|-------|
| **gTTS** | Primary (1st) | Needs Google access | Medium | Fast, simple; fails in China without VPN |
| **edge-tts** | Fallback (2nd) | No VPN needed | Good | Microsoft Edge neural voices; works in China |

**Auto-fallback logic:** Try gTTS first -> if it fails -> automatically switch to edge-tts.

### gTTS Usage (Primary)

```python
from gtts import gTTS
tts = gTTS(text=news_text, lang='en', slow=False)
tts.save('output.mp3')
```

- `lang='en'` for English
- `lang='zh-CN'` for Mandarin Chinese
- `slow=False` for natural reading speed
- Typical output: ~1.7 MB for a 3-4 minute news item

### edge-tts Usage (Fallback)

```python
import edge_tts
import asyncio

VOICE_MAP = {
    'en': 'en-US-AvaNeural',        # Female, US English
    'en-GB': 'en-GB-SoniaNeural',   # Female, British English
    'zh-CN': 'zh-CN-XiaoxiaoNeural', # Female, Mandarin Chinese
}

async def generate(text, output_path, voice='en-US-AvaNeural'):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

asyncio.run(generate(cleaned_text, 'output.mp3'))
```

- List available voices: `edge-tts --list-voices`
- Typical output: ~2-3 MB for a 3-4 minute news item
- Advantage: No Google dependency, works in mainland China

### Using the Unified Interface

```python
from scripts.nature_news_digest import generate_tts_audio

# Auto mode: gTTS -> edge-tts fallback
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='auto')

# Force specific engine
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='edge-tts')
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='gtts')
```

- `generate_tts_audio(...)` prepares the text and tries gTTS first, then edge-tts if needed
- It ensures the local runtime under `scripts/.venv` is ready before audio generation starts
- It runs audio generation through the Python interpreter inside that local runtime

