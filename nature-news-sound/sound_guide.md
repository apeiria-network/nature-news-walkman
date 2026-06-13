# Sound Command Guide

This document contains the detailed instructions for the `/nature-news-sound` command.

## Command

### `/nature-news-sound [user requirements]`
- First present the shared top-10 news shortlist as summaries
- Then output the **full original English text** only for the article(s) the user selects
- Generate and send **English full-text audio** only for the selected article(s)
- Audio save-path logic stays the same as the current skill

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-sound choose space-related news, suitable for listening practice`
- `/nature-news-sound cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-sound climate topic, natural speaking style`

The command name controls the output mode. The trailing text controls customization.

## When to Use
- User asks for "Nature最新新闻" / "Nature news"
- User wants English summaries of Nature news
- User wants full English text of Nature news
- User wants English listening practice with Nature news audio
- User uses `/nature-news-sound`

## Shared Retrieval Reference

Use the shared retrieval logic in [search_guide.md](search_guide.md).

That shared guide covers:
- Latest Nature news discovery
- Top-10 shortlist ranking rules
- Structured summary-cache management
- Retry behavior
- Cache reuse policy
- Shared notes for skipped items, paywalls, and fetch failures

## Interaction Flow for `sound`

1. Retrieve or reuse the shared top-10 summary shortlist
2. Present the top-10 summary text to the user in ranking order
3. Ask the user to choose one or more article numbers, and wait until user provides an answer
4. Fetch or reuse the **full original English text** only for the selected article(s)
5. Output the selected full English text
6. Generate English full-text audio only for the selected article(s)
7. If the user asks for Chinese support, add it after each selected English original text

## Shortlist Output Template

```text
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Summary
{75-100 word English summary}

[Optional Chinese Notes]
{Chinese key points / Chinese explanation only if the user asked for them}
```

## Selected Article Output Template

```text
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Full English Text
{Full original English text from the news page}

[Optional Chinese Notes]
{Chinese key points / Chinese explanation only if the user asked for them}

Audio
Nature_Article{N}_English.mp3
```

## Audio Generation Rules (`sound` only)

For each selected news item in `sound` mode:

1. Prepare the English text for TTS:
   - Remove markdown formatting (*, **, #, etc.)
   - Remove credit lines ("Credit: ...")
   - Remove image references
   - Collapse excessive whitespace

2. Before generating audio, prepare the Python runtime in the skill root:
   - Always prefer an existing `.venv` under the skill root
   - A reusable `.venv` must use Python **3.10–3.14**
   - If that `.venv` is missing required dependencies, install the missing dependencies into **that same `.venv`**
   - If no suitable local `.venv` exists, create `.venv` under the skill root with Python **3.10–3.14**
   - Install all runtime dependencies for this skill only into the skill-local `.venv`
   - Do **not** install dependencies into system Python, user site-packages, or any environment outside the skill root

3. Generate audio with **auto-fallback** (gTTS → edge-tts):

   **Primary: gTTS** (requires Google access):
   ```python
   from gtts import gTTS
   tts = gTTS(text=cleaned_english_text, lang='en', slow=False)
   tts.save(f'D:/nature-news-digest-sounds/Nature_Article{N}_English.mp3')
   ```

   **Fallback: edge-tts** (works in China, no VPN needed):
   ```python
   import edge_tts, asyncio
   async def _gen(text, path):
       com = edge_tts.Communicate(text, 'en-US-AvaNeural')
       await com.save(path)
   asyncio.run(_gen(cleaned_english_text, f'D:/nature-news-digest-sounds/Nature_Article{N}_English.mp3'))
   ```

   Or use the unified helper (auto-fallback built in, local `.venv` enforced):
   ```python
   from scripts.nature_digest import generate_tts_audio
   success, engine = generate_tts_audio(text, output_path, lang='en', engine='auto')
   ```

   **Fallback logic**: Try gTTS first. If gTTS fails (e.g., Google blocked in China), automatically switch to edge-tts. Log which engine was used.

4. Save each file as: `Nature_Article{N}_English.mp3` in `D:/nature-news-digest-sounds` by default; if `D:` is unavailable or not writable, fall back to `C:/nature-news-digest-sounds`
5. When presenting results, send newly generated audio as actual `.mp3` files. Do **not** send audio content as text, transcript, or a language-only description.
6. If file delivery fails, explicitly tell the user the current saved file path so they can retrieve the audio manually.

## Present Results

1. Deliver the shortlist summary text directly in the conversation before article selection
2. After the user selects article numbers, deliver the selected full-text result directly in the conversation
3. For `sound`, send newly generated audio for the selected article(s) as `.mp3` files
4. Do not write the text result to a markdown file
5. If file delivery fails, tell the user the current saved path of each generated audio file
6. Follow the shared retrieval guide for batch freshness, skipped items, paywall notes, and fetch-failure notes
7. Preserve the user's trailing text requirements for possible later mode switches

## Error Handling

- Follow the shared retrieval guide for retrieval-related failures
- **Local `.venv` missing or incomplete**: Reuse the existing skill-local `.venv` when valid; otherwise create `.venv` under the skill root with Python 3.10–3.14 and install any missing required dependencies only into that `.venv`.
- **Local `.venv` version invalid**: If the existing skill-local `.venv` is not Python 3.10–3.14, do not use any external environment; report the issue and recreate the local `.venv` under the skill root.
- **gTTS fails (Google blocked)**: Automatically fall back to edge-tts within the prepared skill-local `.venv`.
- **edge-tts also fails**: Inform the user that both TTS engines failed and suggest checking network or the skill-local `.venv` dependencies.
- **Audio file delivery fails**: Inform the user that file delivery failed and provide the current saved path for each generated audio file.
