---
name: nature-news-sound
description: Provide a listen-and-read Nature news skill. First check whether an existing shortlist cache fits the user's current request, then either reuse that shortlist or retrieve a fresh one. Show summary previews first, wait for the user to choose news numbers, then deliver the full original English text and English mp3 audio only for the selected news items. Use when the user wants Nature news listening practice, news audio narration, or `/nature-news-sound`.
agent_created: true
---

# Nature News Sound

Provide a listen-and-read Nature news experience built around a reusable top-10 shortlist.

## When to Use

- User wants English listening practice from recent Nature news
- User wants `.mp3` audio narration for selected Nature news items
- User wants to preview a shortlist before choosing which news item to hear and read
- User uses `/nature-news-sound`

## Command

### `/nature-news-sound [user requirements]`
- First check whether the latest shortlist cache already fits the user's current request
- Reuse the cached shortlist when it is still a good match; otherwise do a fresh retrieval
- Present up to 10 ranked shortlist summaries first
- Ask the user to choose one or more news numbers and wait for the reply
- Output the **full original English text** only for the selected news item(s)
- Generate and send **English full-text audio** only for the selected news item(s)

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-sound choose space-related news, suitable for listening practice`
- `/nature-news-sound cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-sound climate topic, natural speaking style`

Use the trailing text to customize topic, difficulty, tone, terminology, and output details.

## Retrieval and Audio References

Use [search_guide.md](references/search_guide.md) for:
- latest Nature news discovery
- top-10 shortlist ranking rules
- structured summary-cache management
- retry behavior
- cache-fit checks and reuse decisions
- notes for skipped items, paywalls, and fetch failures
- the default project storage directory `.claude/nature-news-walkman/`

Use [TTS_guide.md](references/TTS_guide.md) for:
- text preparation for TTS
- the local runtime under `scripts/.venv`
- Python version guidance for the sound runtime
- audio-generation guidance
- engine fallback behavior

## Interaction Flow

1. Check whether the latest shortlist cache fits the current request
2. Reuse the cached shortlist if it fits; otherwise retrieve a fresh shortlist
3. Present the shortlist summaries to the user in ranking order
4. Ask the user to choose one or more news numbers, then wait for the reply
5. Fetch or reuse the **full original English text** only for the selected news item(s)
6. Output the selected full English text
7. Generate English full-text audio only for the selected news item(s)
8. If the user asks for Chinese support, add it after each selected English text

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

## Selected News Output Template

```text
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Full English Text
{Full original English text from the news page}

[Optional Chinese Notes]
{Chinese key points / Chinese explanation only if the user asked for them}

Audio
Nature_News{N}_English.mp3
```

## Audio Generation Rules

For each selected news item:
- Prepare the English text for TTS before audio generation
- Follow [TTS_guide.md](references/TTS_guide.md) for engine selection and fallback behavior
- Generate audio with automatic fallback from gTTS to edge-tts when needed
- Save each file as `Nature_News{N}_English.mp3`
- Send newly generated audio as actual `.mp3` files
- If file delivery fails, explicitly tell the user the current saved file path so the audio can be retrieved manually

## Present Results

1. Deliver the shortlist summary text directly in the conversation before news selection
2. After the user selects news numbers, deliver the selected full-text result directly in the conversation
3. For `sound`, send newly generated audio for the selected news item(s) as `.mp3` files
4. Do not write the text result to a markdown file
5. If file delivery fails, tell the user the current saved path of each generated audio file
6. Briefly say whether the shortlist was reused from cache or freshly retrieved
7. Note any skipped items, paywall limitations, or fetch failures
8. Apply the user's trailing requirements consistently when ranking the shortlist and presenting selected full text

## Error Handling

- Follow [search_guide.md](references/search_guide.md) for retrieval-related failures
- Follow [TTS_guide.md](references/TTS_guide.md) for TTS fallback behavior
- If both TTS engines fail, inform the user and suggest checking network availability or local Python dependencies
- If audio file delivery fails, inform the user and provide the current saved path for each generated audio file
