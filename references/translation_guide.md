# Nature News TTS Reference

This reference is only for English TTS generation used by `/nature-news-sound`.

## TTS Guidelines

### Local Python Environment
- Always prefer the existing `.venv` under the skill root before generating audio
- A reusable local `.venv` must use Python **3.10–3.14**
- If the local `.venv` is missing required dependencies, install the missing dependencies into **that same `.venv`**
- If no suitable local `.venv` exists, create `.venv` under the skill root with Python **3.10–3.14**
- Install all runtime dependencies only into the skill-local `.venv`
- Do **not** install dependencies into system Python, global site-packages, user site-packages, or any environment outside the skill root

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
tts = gTTS(text=article_text, lang='en', slow=False)
tts.save('output.mp3')
```

- `lang='en'` for English
- `lang='zh-CN'` for Mandarin Chinese
- `slow=False` for natural reading speed
- Typical output: ~1.7 MB for a 3-4 minute article

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

- Install inside the skill-local `.venv` only
- List available voices: `edge-tts --list-voices`
- Typical output: ~2-3 MB for a 3-4 minute article
- Advantage: No Google dependency, works in mainland China

### Using the Unified Interface

```python
from scripts.nature_digest import generate_tts_audio

# Auto mode: gTTS -> edge-tts fallback
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='auto')

# Force specific engine
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='edge-tts')
success, engine = generate_tts_audio(text, 'output.mp3', lang='en', engine='gtts')
```

- `generate_tts_audio(...)` will first prepare the skill-local `.venv`
- It reuses `.venv` when the Python version is 3.10–3.14 and installs any missing required dependencies into that same environment
- It does not use or modify Python environments outside the skill root

