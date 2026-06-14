# Nature News Walkman

A Claude-oriented Nature news toolkit with three modes built on the same shortlist workflow: **brief**, **text**, and **sound**. It helps you discover recent Nature news, reuse a cached shortlist when it still fits the request, and then deliver summaries, full text, or generated audio depending on the selected mode.

## Table of Contents

- [Overview](#overview)
- [Modes](#modes)
- [Slash Commands](#slash-commands)
- [Shared Shortlist and Storage Behavior](#shared-shortlist-and-storage-behavior)
- [Documentation Map](#documentation-map)
- [Notes on Audio Mode](#notes-on-audio-mode)

## Overview

This project organizes recent Nature news into a reusable top-10 shortlist and exposes that shortlist through three user-facing skills:

- **brief**: summary-first reading
- **text**: shortlist first, then full original English text for selected items
- **sound**: shortlist first, then full text plus generated English MP3 audio for selected items

The three modes share the same general flow:

1. Check whether a recent shortlist cache still fits the current request.
2. Reuse the cache when it is still a good match.
3. Otherwise fetch a fresh batch of recent Nature news.
4. Present results in the mode-specific format.

## Modes

### `nature-news-brief`

Use this mode when the user wants a compact digest.

- Presents up to 10 ranked Nature news items
- Each item includes summary-stage information such as title, date, source, and English summary
- Optional Chinese notes can be added when requested

See: [nature-news-brief/SKILL.md](nature-news-brief/SKILL.md)

### `nature-news-text`

Use this mode when the user wants to read full original English content.

- Presents shortlist summaries first
- Waits for the user to choose one or more news items
- Returns the **full original English text** only for the selected items
- Optional Chinese notes can be added after the English text

See: [nature-news-text/SKILL.md](nature-news-text/SKILL.md)

### `nature-news-sound`

Use this mode when the user wants listening practice or narrated audio.

- Presents shortlist summaries first
- Waits for the user to choose one or more news items
- Returns the selected **full original English text**
- Generates and sends **English MP3 audio** for the selected items

See: [nature-news-sound/SKILL.md](nature-news-sound/SKILL.md)

## Slash Commands

### Generic forms

- `/nature-news-brief [user requirements]`
- `/nature-news-text [user requirements]`
- `/nature-news-sound [user requirements]`

### Examples

- `/nature-news-brief easier English, climate topic, scientific tone`
- `/nature-news-text keep the original wording, choose one space-related article`
- `/nature-news-sound cancer biology, natural speaking style, add Chinese key points`

Any trailing text after the command is treated as part of the user's request and can shape topic, difficulty, tone, terminology, and output details.

## Shared Shortlist and Storage Behavior

All three modes work from a structured shortlist cache and shared retrieval rules.

- The shortlist cache file is `Nature_LatestBatch_Cache.json`
- The default project storage directory is `.claude/nature-news-walkman/`
- This directory is used for shortlist cache and generated outputs such as audio
- Before saving shortlist cache, the workflow should tell the user which storage path will be used

For deeper retrieval and cache rules, see the mode-specific guides below.

## Documentation Map

### Skill entry points

- [nature-news-brief/SKILL.md](nature-news-brief/SKILL.md)
- [nature-news-text/SKILL.md](nature-news-text/SKILL.md)
- [nature-news-sound/SKILL.md](nature-news-sound/SKILL.md)

### Retrieval and cache guides

- [nature-news-brief/references/search_guide.md](nature-news-brief/references/search_guide.md)
- [nature-news-text/references/search_guide.md](nature-news-text/references/search_guide.md)
- [nature-news-sound/references/search_guide.md](nature-news-sound/references/search_guide.md)

### Sound / TTS details

- [nature-news-sound/references/TTS_guide.md](nature-news-sound/references/TTS_guide.md)

## Notes on Audio Mode

The `nature-news-sound` mode uses a local runtime under `scripts/.venv` for audio generation. Detailed setup, engine behavior, and troubleshooting notes are documented in the sound mode TTS guide rather than repeated here.
