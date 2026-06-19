---
name: nature-news-walkman
description: Retrieve recent Nature NEWS articles, summarize them in English, ask the user to choose article numbers, then generate English TTS audio for the selected full texts. Use when the user wants Nature news reading-plus-listening practice or `/nature-news-walkman`.
---

# Nature News Walkman

Provide a summary-first Nature NEWS workflow built on the project-level helper scripts in [scripts/](scripts/).

## When to Use

- User wants recent Nature NEWS articles for English reading or listening practice
- User wants shortlist summaries before choosing which items to hear
- User wants English mp3 audio for selected Nature news articles
- User uses `/nature-news-walkman`

## Command

### `/nature-news-walkman [user requirements]`

Any trailing text after the command is part of the user's request.

Examples:
- `/nature-news-walkman latest neuroscience news`
- `/nature-news-walkman choose easier-to-read articles for English learning`
- `/nature-news-walkman climate and health topics, then make audio for the one I choose`

## Core Workflow

1. Ensure the local Python environment is ready by running `bash scripts/venv_install.sh` when needed.
2. Retrieve the current Nature RSS feed with `python scripts/rss_fetch.py`.
3. Fetch article pages with `python scripts/fetch_nature_article.py`.
   - Default behavior reads only the publicly visible article content.
   - If the user provides a local cookie file, the script may use it to fetch more complete article text.
   - Only pages with the `NEWS` marker are kept.
   - Batch fetches wait 5-10 seconds between requests.
4. Read the fetched article list with `python scripts/news_read.py`.
5. Summarize the shortlisted articles in English and present them in numbered order.
6. Ask the user to choose one or more article numbers.
7. After the user selects numbers, generate English audio with `python scripts/nature_news_sound.py <numbers>`.
8. Return the generated mp3 file paths, and send the audio files when the environment supports file delivery.

## Required Interaction Rules

- Always present summaries before generating audio.
- Always wait for the user's numeric selection before creating audio.
- Keep the shortlist in ranking order and preserve article indices.
- Do not generate audio for unselected articles.
- If the user asks for multiple items, generate audio for all selected indices in one run.

## Script Responsibilities

- [scripts/venv_install.sh](scripts/venv_install.sh): create `scripts/.venv` and install required Python packages
- [scripts/rss_fetch.py](scripts/rss_fetch.py): download the current Nature RSS feed and extract article URLs
- [scripts/fetch_nature_article.py](scripts/fetch_nature_article.py): fetch article metadata and body text, filter to `NEWS`, optionally use a user-provided cookie file, and save structured JSON
- [scripts/news_read.py](scripts/news_read.py): print structured article text for model reading, ordered newest-first and capped to 10 items
- [scripts/nature_news_sound.py](scripts/nature_news_sound.py): generate English TTS mp3 files for selected article indices

## References

Use [reference/web_fetch_guide.md](reference/web_fetch_guide.md) for:
- environment bootstrap expectations
- RSS retrieval
- URL filtering
- `NEWS`-only article selection
- optional cookie-file usage
- fetch limits, delays, and output locations
- summary-stage article reading rules

Use [reference/audio_tts_guide.md](reference/audio_tts_guide.md) for:
- TTS engine behavior
- audio file naming and storage
- text cleaning for speech
- `gTTS` / `edge-tts` / `auto` behavior
- user-selection-to-audio workflow

## Output Expectations

### Summary Stage

Present the fetched shortlist in English, in numbered order, with at least:
- title
- author
- URL
- a short English summary based on the fetched article text

Then ask the user to choose article numbers.

### Audio Stage

After the user selects numbers:
- generate audio for those indices only
- report the saved mp3 paths
- if audio cannot be delivered directly, tell the user where the files were saved

## Default Storage

All helper scripts write output under a `nature-news-walkman/` subdirectory inside the project's active workspace folder. The workspace folder is determined at runtime and is typically the first writable directory that follows the project's tool convention, such as `.claude/`, `.workbuddy/`, or a similar platform-specific folder.

Typical subdirectories:
- `<workspace>/nature-news-walkman/tmp/` — RSS text and URL lists
- `<workspace>/nature-news-walkman/data/` — fetched article JSON
- `<workspace>/nature-news-walkman/audio/` — generated mp3 files

## Error Handling

- If RSS fetch fails, tell the user and stop.
- If article fetch returns no `NEWS` pages, tell the user and stop.
- If cookie-based fetch is requested but the cookie file is missing or invalid, fall back only when the user's intent allows public-only content; otherwise explain the failure.
- If TTS generation fails with `gTTS`, use fallback behavior described in [reference/audio_tts_guide.md](reference/audio_tts_guide.md).
- If both TTS engines fail, report the failure and the current output path state.
