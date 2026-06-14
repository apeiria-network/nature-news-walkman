---
name: nature-news-text
description: Provide a full-text Nature news reading skill. First check whether an existing shortlist cache fits the user's current request, then either reuse that shortlist or retrieve a fresh one. Show summary previews first, wait for the user to choose news numbers, and then deliver the full original English text only for the selected news items. Use when the user wants full news text, English reading practice, or `/nature-news-text`.
agent_created: true
---

# Nature News Text

Provide a full-text Nature news reading experience built around a top-10 shortlist that can be reused when it still fits the user's request.

## When to Use

- User wants the full original English text of recent Nature news
- User wants English reading practice with complete news items instead of summaries only
- User wants to preview a shortlist before choosing which news item to read
- User uses `/nature-news-text`

## Command

### `/nature-news-text [user requirements]`
- First check whether the latest shortlist cache already fits the user's current request
- Reuse the cached shortlist when it is still a good match; otherwise do a fresh retrieval
- Present up to 10 ranked shortlist summaries first
- Ask the user to choose one or more news numbers and wait for the reply
- Output the **full original English text** only for the selected news item(s)
- Do not replace the selected news text with a summary unless the user explicitly asks

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-text cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-text climate topic, keep the original wording`
- `/nature-news-text choose space-related news, suitable for reading practice`

Use the trailing text to customize topic, difficulty, tone, terminology, and output details.

## Retrieval and Cache Guide

Use [search_guide.md](references/search_guide.md) for:
- latest Nature news discovery
- top-10 shortlist ranking rules
- structured shortlist-cache management
- retry behavior
- cache-fit checks and reuse decisions
- notes for skipped items, paywalls, and fetch failures
- the default project storage directory `.claude/nature-news-walkman/`

## Interaction Flow

1. Check whether the latest shortlist cache fits the current request
2. Reuse the cached shortlist if it fits; otherwise retrieve a fresh shortlist
3. Present the shortlist summaries to the user in ranking order
4. Ask the user to choose one or more news numbers, then wait for the reply
5. Fetch or reuse the **full original English text** only for the selected news item(s)
6. Output the selected full English text
7. If the user asks for Chinese support, add it after each selected English text

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
```

## Present Results

1. Deliver the shortlist summary text directly in the conversation before news selection
2. After the user selects news numbers, deliver the selected full-text result directly in the conversation
3. Do not write the text result to a markdown file
4. Briefly say whether the shortlist was reused from cache or freshly retrieved
5. Note any skipped items, paywall limitations, or fetch failures
6. Apply the user's trailing requirements consistently when ranking the shortlist and presenting selected full text

## Error Handling

- Follow [search_guide.md](references/search_guide.md) for retrieval-related failures
- If the user asks for both full text and extra annotations, keep the original English text as the primary output and place extra annotations after it

