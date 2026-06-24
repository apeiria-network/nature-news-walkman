# Nature News Walkman Audio TTS Guide

This guide describes how `nature-news-walkman` should generate English TTS audio for selected Nature NEWS articles.

## Scope

Use this guide for the audio half of the workflow:
- TTS text preparation
- engine selection and fallback
- speed control behavior
- audio file naming and storage
- user-selection-to-audio flow
- error handling for audio failures

The web fetch and article reading flow belongs in [web_fetch_guide.md](web_fetch_guide.md).
The command and interaction contract belong in [SKILL.md](../SKILL.md).

## TTS Prerequisites

The local Python environment must be ready before generating audio.
If `scripts/.venv` does not exist, run:

```sh
bash scripts/venv_install.sh
```

The audio script `scripts/nature_news_sound.py` locates the venv interpreter at `scripts/.venv/Scripts/python.exe` (Windows) or `scripts/.venv/bin/python` (Unix).

If the interpreter is not found, the script exits with an error and instructs the user to run the install script first.

## Audio Generation Command

After the user selects article numbers from the shortlist, run:

```sh
python scripts/nature_news_sound.py <index1> [<index2> ...]
```

Indices are 1-based and correspond to the positions from `news_read.py` output.

Examples:

```sh
# Generate audio for article 2 only
python scripts/nature_news_sound.py 2

# Generate audio for articles 1, 3, and 5
python scripts/nature_news_sound.py 1 3 5

# Generate slower audio
python scripts/nature_news_sound.py 2 --speed 0.8

# Generate faster audio
python scripts/nature_news_sound.py 2 --speed 1.25
```

## TTS Engine Selection

| Engine | Priority | Network | Quality | Notes |
|--------|----------|---------|---------|-------|
| **edge-tts** | Primary (1st) | No VPN needed | Good | Microsoft Edge neural voices; supports numeric speed control; works in China |
| **gTTS** | Fallback (2nd) | Needs Google access | Medium | Simple fallback; fails in China without VPN; only supports `slow=True/False` |

### `--engine` argument

| Value | Behavior |
|-------|----------|
| `auto` | Try edge-tts first, fall back to gTTS on failure (default) |
| `gtts` | Use gTTS only |
| `edge-tts` | Use edge-tts only |

Examples:

```sh
# Auto mode (recommended)
python scripts/nature_news_sound.py 1 2

# Force edge-tts
python scripts/nature_news_sound.py 1 2 --engine edge-tts

# Force gTTS
python scripts/nature_news_sound.py 1 2 --engine gtts
```

### Auto-fallback behavior

When `--engine auto`:
1. Try edge-tts
2. If edge-tts fails, automatically switch to gTTS
3. Report which engine was used per article
4. If the requested speed cannot be matched exactly by gTTS, print a clear downgrade note

## Speech Speed Control

`scripts/nature_news_sound.py` accepts an optional numeric speed multiplier through `--speed`.

- Omit `--speed` to use the selected engine's default speaking rate
- `--speed 1.0` also means default speed
- Values below `1.0` request slower speech, for example:
  - `0.75` = about 0.75x speed
  - `0.8` = about 0.8x speed
- Values above `1.0` request faster speech, for example:
  - `1.1` = about 1.1x speed
  - `1.25` = about 1.25x speed

### LLM-side defaults for vague requests

The script only accepts the final numeric speed value.
If the user says only “slower” or “faster” without a multiplier, the calling LLM should translate that request before invoking the script:

- “slower” → `--speed 0.75`
- “faster” → `--speed 1.25`

### Engine-specific speed mapping

#### edge-tts

`edge-tts` supports percentage-based rate control, so the script converts the multiplier relative to default speed.

Examples:
- `0.75` → `-25%`
- `0.8` → `-20%`
- `1.1` → `+10%`
- `1.25` → `+25%`

When speed is omitted or equals `1.0`, the script should not pass an explicit rate override.

#### gTTS

`gTTS` does not support arbitrary numeric speed values.
It only supports a `slow=True/False` switch, so the script degrades as follows:

- speed omitted or `>= 1.0` → use default speed (`slow=False`)
- speed `< 1.0` → use slow mode (`slow=True`)

Important limitations:
- `gTTS` cannot precisely match values such as `0.8x` or `0.9x`; it can only approximate them with slow mode
- `gTTS` cannot accelerate speech above default speed
- When a requested speed cannot be matched exactly, the script should tell the user what fallback behavior was used

## Edge-TTS Voice Mapping

| Language | Voice |
|----------|-------|
| `en` | `en-US-AvaNeural` (Female, US English) |
| `en-US` | `en-US-AvaNeural` |
| `en-GB` | `en-GB-SoniaNeural` (Female, British English) |
| `zh-CN` | `zh-CN-XiaoxiaoNeural` (Female, Mandarin Chinese) |
| `zh` | `zh-CN-XiaoxiaoNeural` |

Default language is English (`en`).

## Text Preparation for TTS

Before sending article body text to a TTS engine, `nature_news_sound.py` applies the following cleaning steps:

1. Remove markdown bold and italic markers (`*`, `**`)
2. Remove markdown links, keeping the link text
3. Remove `Credit: ...` lines
4. Remove image references
5. Remove markdown heading markers (`#`, `##`, etc.)
6. Remove horizontal rules (`---`)
7. Remove `doi:` and `Source:` lines
8. Unwrap bracketed notes such as `[in vitro]`
9. Collapse excessive blank lines
10. Collapse multiple spaces

Section headings preserved in the article body text (such as `Just chilling` or `Inconsistent rules`) are passed through to TTS as plain text, so they are read aloud as natural paragraph breaks.

## Audio File Naming and Storage

Audio files are saved to:

```
<your workspace>/nature-news-walkman/audio/
```

Each file is named using the 1-based article index and a slug derived from the article title:

```
{index:03d}_{title-slug}.mp3
```

Examples:

```
001_freezing-brain-damage-in-its-tracks-cooling-drugs-limit-stro.mp3
005_how-the-brain-builds-sentences-neuron-by-neuron.mp3
```

## User-Selection-to-Audio Flow

1. Wait for the user to provide article indices (numbers from the summary stage)
2. If the user requested a speaking speed, convert that intent into a numeric `--speed` value before calling the script
3. Run `nature_news_sound.py` with those indices
4. The script reads the fetched article JSON sorted newest-first, the same order as `news_read.py`
5. For each selected index, extract `full_text` and generate audio
6. Report each saved file path

Example output:

```
[2] Freezing brain damage in its tracks: cooling drugs limit stroke injury in mice
  Trying edge-tts at 0.8x speed (rate -20%)... OK
  Saved: <your workspace>/nature-news-walkman/audio/002_freezing-brain-damage-in-its-tracks-cooling-drugs-limit-stro.mp3 (edge-tts, 0.8x speed)

Done. 1 file(s) generated.
```

## File Delivery

After audio generation:
- send or link the generated mp3 files when the environment supports file delivery
- if file delivery fails, tell the user the saved file path so the audio can be retrieved manually

## Error Handling

- **edge-tts failure in `auto` mode**: automatically switch to gTTS and report the fallback
- **Requested speed slower than 1.0 with gTTS**: explain that gTTS is approximating the request with `slow=True`
- **Requested speed faster than 1.0 with gTTS**: explain that gTTS does not support acceleration and that default speed was used instead
- **Both engines fail**: report the failure explicitly, list the saved state if any partial files exist, and suggest checking network availability or running `bash scripts/venv_install.sh` to verify dependencies
- **Article index out of range**: skip that index, print a warning, and continue with valid indices
- **Article body text is empty**: skip that article and print a warning
- **venv not found**: print a clear error message instructing the user to run `bash scripts/venv_install.sh`

## Representative Commands

```sh
# Single article, auto engine
python scripts/nature_news_sound.py 2

# Multiple articles, auto engine
python scripts/nature_news_sound.py 1 3 5

# Slow down speech
python scripts/nature_news_sound.py 2 --speed 0.8

# Speed up speech
python scripts/nature_news_sound.py 2 --speed 1.25

# Force edge-tts (China / no VPN)
python scripts/nature_news_sound.py 2 --engine edge-tts

# Force gTTS with a slower request (approximated by slow=True)
python scripts/nature_news_sound.py 2 --engine gtts --speed 0.8

# Use a different input JSON
python scripts/nature_news_sound.py 1 --input <your workspace>/nature-news-walkman/temp/nature_articles.json

# Use a different output directory
python scripts/nature_news_sound.py 1 --output-dir <your workspace>/nature-news-walkman/audio
```
