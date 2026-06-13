---
name: nature-news-sound
description: Provide a listen-and-read Nature news skill. Fetch or reuse the latest top Nature news shortlist, present summary previews first, then deliver the full original English text and English mp3 audio only for the article numbers the user selects. Use when the user wants Nature news listening practice, article audio narration, or `/nature-news-sound`.
agent_created: true
---

# Nature News Sound

Provide a listen-and-read Nature news experience built around a reusable top-10 shortlist.

## When to Use

- User wants English listening practice from recent Nature news
- User wants `.mp3` audio narration for selected Nature news articles
- User wants to preview a shortlist before choosing which article to hear and read
- User uses `/nature-news-sound`

## Command

### `/nature-news-sound [user requirements]`
- First present the shared top-10 news shortlist as summaries
- Then output the **full original English text** only for the article(s) the user selects
- Generate and send **English full-text audio** only for the selected article(s)

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-sound choose space-related news, suitable for listening practice`
- `/nature-news-sound cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-sound climate topic, natural speaking style`

The command name controls the output mode. The trailing text controls customization.

## Shared References

Use the shared retrieval logic in [search_guide.md](../references/search_guide.md).

For detailed TTS runtime, local `.venv`, engine fallback, and audio-generation guidance, use [TTS_guide.md](../references/TTS_guide.md).

The shared guides cover:
- Latest Nature news discovery
- Top-10 shortlist ranking rules
- Structured summary-cache management
- Retry behavior
- Cache reuse policy
- Shared notes for skipped items, paywalls, and fetch failures
- TTS preparation, local runtime requirements, and engine fallback behavior

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

For each selected news item in `sound`:
- Prepare the English text for TTS before audio generation
- Use the shared TTS reference for local `.venv` requirements and engine selection
- Generate audio with automatic fallback from gTTS to edge-tts when needed
- Save each file as `Nature_Article{N}_English.mp3`
- Send newly generated audio as actual `.mp3` files
- If file delivery fails, explicitly tell the user the current saved file path so the audio can be retrieved manually

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
- Follow the shared TTS reference for local runtime recovery and engine fallback behavior
- If both TTS engines fail, inform the user and suggest checking network availability or the local runtime dependencies
- If audio file delivery fails, inform the user and provide the current saved path for each generated audio file
