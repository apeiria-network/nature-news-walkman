---
name: nature-news-digest
description: Fetch the latest top trending news from Nature, have the LLM generate a line-by-line bilingual (English-Chinese) text response directly in the conversation, and produce English TTS audio readings for each article. Use when the user asks for Nature news, science news digest, bilingual translation of scientific articles, or news with audio narration.
agent_created: true
---

# Nature News Digest

Fetch Nature's top trending news, have the LLM produce a line-by-line EN-CN bilingual response directly in the conversation, and generate English audio readings.

## When to Use

- User asks for "Nature最新新闻" / "Nature news" / "science news"
- User wants bilingual translation of scientific articles
- User wants news articles read aloud (TTS audio)
- User says "nature-news-digest" or similar triggers

## Workflow

### Step 1: Search & Identify Top Articles

1. Use **WebSearch** to find the latest Nature news articles
   - Query: `"Nature" latest news` with `topic: news`
   - Or query keyword groups: `["Nature journal latest news", "Nature news trending articles"]`

2. Use **WebFetch** on `https://www.nature.com/news` to get the featured/trending articles list
   - Identify the top 3 articles by editorial prominence (hero images, top placement)
   - For each article, record: title, URL, date, brief description

3. Present a summary table to the user:
   | # | Title | Author | Date |

### Step 2: Fetch Full Article Content

For **each** of the top 3 articles (run WebFetch calls in parallel):

1. **WebFetch** the article URL
   - Prompt: "Extract the FULL article text in English, including: the complete title, author names, publication date, all paragraphs of the main body text. Return the complete original English text as-is, do not summarize or translate."
   - If a fetch fails, retry once. If still failing, skip that article and note the failure.

2. Store the full English text for each article.

### Step 3: Generate the Bilingual Response with the LLM

For each article, translate **line by line** and have the LLM present the final bilingual result directly in the conversation.

**Output contract:**
1. Output articles in order: `Article 1`, `Article 2`, `Article 3`
2. For each article, use this fixed section order:
   - `Article {N}: {English Title}`
   - `Title: {English}`
   - `标题： {Chinese}`
   - `Author: {Name}`
   - `作者： {Name}`
   - `Publication Date: {EN date}`
   - `发布日期： {CN date}`
   - `Source: {URL}`
   - `来源： {URL}`
   - `Summary / 摘要`
   - `Full Text / 正文`
3. In `Full Text / 正文`, format the response as alternating lines: **one English line, one Chinese line**
4. Keep each Chinese line directly under its corresponding English line
5. Preserve the original article order and do not merge multiple articles into one block
6. Do not summarize in place of the full text unless the article body is unavailable
7. If a section is missing from the source page, omit that section rather than inventing content
8. Send the bilingual result directly to the user in the conversation instead of writing a markdown file

**Translation rules** (see references/translation_guide.md for terminology):
- Keep proper nouns (names, institutions) in English
- Add Chinese equivalent in parentheses on first occurrence of technical terms
- Translate quotes and attributions naturally
- Sub-headings format: `English Heading / 中文标题`
- Metadata format:
  ```
  Title: {English}
  标题： {Chinese}

  Author: {Name}
  作者： {Name}

  Publication Date: {EN date}
  发布日期： {CN date}
  ```


### Step 4: Generate English TTS Audio

For **each** article (can run in parallel):

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

### Step 5: Present Results

1. Send the bilingual text response directly in the conversation
2. Send newly generated audio to the user as `.mp3` files, not as prose descriptions or text transcripts
3. If file delivery fails, tell the user the current saved path of each generated audio file
4. Summarize what was generated:
   - Audio files generated (count, sizes)
   - Any articles that had paywall limitations or fetch failures

## Error Handling

- **WebFetch fails**: Retry once. If still failing, skip the article and inform the user.
- **Local `.venv` missing or incomplete**: Reuse the existing skill-local `.venv` when valid; otherwise create `.venv` under the skill root with Python 3.10–3.14 and install any missing required dependencies only into that `.venv`.
- **Local `.venv` version invalid**: If the existing skill-local `.venv` is not Python 3.10–3.14, do not use any external environment; report the issue and recreate the local `.venv` under the skill root.
- **gTTS fails (Google blocked)**: Automatically fall back to edge-tts within the prepared skill-local `.venv`.
- **edge-tts also fails**: Inform the user that both TTS engines failed and suggest checking network or the skill-local `.venv` dependencies.
- **Audio file delivery fails**: Inform the user that file delivery failed and provide the current saved path for each generated audio file.
- **Paywalled content**: Extract all freely visible text. Add a note at the end of the article.
- **Empty article**: If an article has no extractable body text, skip it and fetch the next most prominent article.

## Output Files

| File | Description |
|------|-------------|
| Nature_Article1_English.mp3 | English TTS audio for Article 1 |
| Nature_Article2_English.mp3 | English TTS audio for Article 2 |
| Nature_Article3_English.mp3 | English TTS audio for Article 3 |

The bilingual result is delivered directly in the conversation. Newly generated audio must be delivered as `.mp3` files. If file delivery fails, report the current saved path to the user. Audio files go to `D:/nature-news-digest-sounds` by default, with fallback to `C:/nature-news-digest-sounds` if needed.
