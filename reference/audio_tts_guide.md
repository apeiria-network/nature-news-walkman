# Nature News Walkman Audio TTS Guide

This guide describes how `nature-news-walkman` should generate English TTS audio for selected Nature NEWS articles.

## Scope

Use this guide for the audio half of the workflow:
- TTS text preparation
- engine selection and fallback
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
```

## TTS Engine Selection

| Engine | Priority | Network | Quality | Notes |
|--------|----------|---------|---------|-------|
| **gTTS** | Primary (1st) | Needs Google access | Medium | Fast, simple; fails in China without VPN |
| **edge-tts** | Fallback (2nd) | No VPN needed | Good | Microsoft Edge neural voices; works in China |

### `--engine` argument

| Value | Behavior |
|-------|----------|
| `auto` | Try gTTS first, fall back to edge-tts on failure (default) |
| `gtts` | Use gTTS only |
| `edge-tts` | Use edge-tts only |

Examples:

```sh
# Auto mode (recommended)
python scripts/nature_news_sound.py 1 2

# Force edge-tts (use when Google is blocked)
python scripts/nature_news_sound.py 1 2 --engine edge-tts

# Force gTTS
python scripts/nature_news_sound.py 1 2 --engine gtts
```

### Auto-fallback behavior

When `--engine auto`:
1. Try gTTS
2. If gTTS fails (network timeout, connection refused, or `gTTSError`), automatically switch to edge-tts
3. Report which engine was used per article

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
<workspace>/nature-news-walkman/audio/
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
2. Run `nature_news_sound.py` with those indices
3. The script reads the fetched article JSON sorted newest-first, the same order as `news_read.py`
4. For each selected index, extract `full_text` and generate audio
5. Report each saved file path

Example output:

```
[2] Freezing brain damage in its tracks: cooling drugs limit stroke injury in mice
  Trying gTTS... failed, trying edge-tts... OK
  Saved: .claude/nature-news-walkman/audio/002_freezing-brain-damage-in-its-tracks-cooling-drugs-limit-stro.mp3

Done. 1 file(s) generated.
```

## File Delivery

After audio generation:
- send or link the generated mp3 files when the environment supports file delivery
- if file delivery fails, tell the user the saved file path so the audio can be retrieved manually

## Error Handling

- **gTTS network timeout or connection refused**: automatically switch to edge-tts in `auto` mode; report the failure in `gtts` mode
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

# Force edge-tts (China / no VPN)
python scripts/nature_news_sound.py 2 --engine edge-tts

# Use a different input JSON
python scripts/nature_news_sound.py 1 --input <workspace>/nature-news-walkman/data/nature_articles.json

# Use a different output directory
python scripts/nature_news_sound.py 1 --output-dir <workspace>/nature-news-walkman/audio
```
