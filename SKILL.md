---
name: nature-news-digest
description: Support three independent Nature news commands: /nature-news-brief, /nature-news-text, and /nature-news-sound. Fetch the latest top Nature news, let the LLM first present a reusable top-10 shortlist of high-heat or high-visibility Nature news summaries, then output summaries, full original English text, or English TTS audio depending on the selected mode. Use when the user asks for Nature news, English reading/listening practice, news summaries, full news text, or news audio narration.
agent_created: true
---

# Nature News Digest

Support 3 independent command modes for Nature news reading and listening practice, built around one shared top-10 shortlist instead of one fixed immediate-output flow.

## When to Use

- User asks for "Nature最新新闻" / "Nature news"
- User wants English summaries of Nature news
- User wants full English text of Nature news
- User wants English listening practice with Nature news audio
- User uses `/nature-news-brief`, `/nature-news-text`, or `/nature-news-sound`

## Command Routing

Determine which command mode the user invoked, then follow the corresponding command guide:

- `/nature-news-brief [user requirements]` → [references/brief_guide.md](references/brief_guide.md)
- `/nature-news-text [user requirements]` → [references/text_guide.md](references/text_guide.md)
- `/nature-news-sound [user requirements]` → [references/sound_guide.md](references/sound_guide.md)

The command name controls the output mode. Any trailing text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-brief easier English, climate topic, scientific tone`
- `/nature-news-text cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-sound choose space-related news, suitable for listening practice`

## Shared Retrieval Logic

All 3 command modes share the same Nature news retrieval and cache-reuse logic.

Use:
- [references/search_guide.md](references/search_guide.md) for shared retrieval, top-10 shortlist ranking rules, cache management, shared presentation notes, and shared retrieval-related error handling

## Command Mode Summary

### `brief`
- Present the shared top-10 shortlist as summaries
- Keep each summary around **75-100 words**
- Do not output the full English text unless the user explicitly asks

### `text`
- Present the shared top-10 shortlist first
- Ask the user to choose one or more article numbers
- Output the **full original English text** only for the selected article(s)

### `sound`
- Present the shared top-10 shortlist first
- Ask the user to choose one or more article numbers
- Output the **full original English text** and generate/send **English full-text audio** only for the selected article(s)
- Use the command-specific guide for TTS preparation, local `.venv` rules, fallback logic, and file delivery behavior

## Output Files

| File | Description |
|------|-------------|
| Nature_Article{N}_English.mp3 | English TTS audio for a selected shortlist article in `sound` mode |
| Nature_LatestBatch_Cache.json | Structured cache of the latest top-10 Nature news shortlist |

Text results are delivered directly in the conversation. Newly generated audio must be delivered as `.mp3` files. If file delivery fails, report the current saved path to the user.

