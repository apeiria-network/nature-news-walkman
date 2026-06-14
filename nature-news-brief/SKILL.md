---
name: nature-news-brief
description: Provide a summary-first Nature news briefing skill. First check whether an existing shortlist cache fits the user's current request, then either reuse that shortlist or retrieve a fresh one. Present up to 10 ranked English summaries with optional Chinese notes. Use when the user wants Nature news summaries, a short reading digest, or `/nature-news-brief`.
agent_created: true
---

# Nature News Brief

Provide a summary-first Nature news briefing experience built around a reusable top-10 shortlist.

## When to Use

- User asks for Nature news summaries or a short digest
- User wants brief English reading practice from recent Nature news
- User wants a ranked shortlist instead of full news text
- User uses `/nature-news-brief`

## Command

### `/nature-news-brief [user requirements]`
- First check whether an existing shortlist cache from a recent run already fits the user's current request
- Reuse the cached shortlist when it is still a good match; otherwise do a fresh retrieval
- Output summary-stage results for up to 10 ranked Nature news items
- Each summary should be about **75-100 words**
- The summary is generated from fetched English news text or other usable summary-stage source text

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-brief easier English, climate topic, scientific tone`
- `/nature-news-brief cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-brief choose space-related news, suitable for reading practice`

Use the trailing text to customize topic, difficulty, tone, terminology, and output details.

## Retrieval and Cache Guide

Use [search_guide.md](references/search_guide.md) for:
- latest Nature news discovery
- top-10 shortlist ranking rules
- structured summary-cache management
- retry behavior
- cache-fit checks and reuse decisions
- notes for skipped items, paywalls, and fetch failures
- the default project storage directory `.claude/nature-news-walkman/`

## Output Rules

For the selected shortlist batch:
- Output `News {N}: {English Title}`
- Include `Publication Date: {Date in English}` when available
- Include `Source: {URL}`
- Output one English summary of about **75-100 words** for each shortlisted item
- If the user asks for Chinese support, add Chinese notes or key points as an extra section
- Do not output the full English text unless the user explicitly asks

This skill should both:
- save the structured top-10 summary shortlist to cache
- send the summary text directly to the user in the conversation

`nature-news-brief` does not require a selection step by default. It is the summary-oriented view of the current shortlist.

## Output Template

```text
News {N}: {English Title}

Publication Date: {Date in English}
Source: {URL}

Summary
{75-100 word English summary}

[Optional Chinese Notes]
{Chinese key points only if the user asked for them}
```

## Present Results

1. Deliver the summary text result directly in the conversation
2. Do not write the text result to a markdown file
3. Present up to **10** shortlisted news summaries in ranking order
4. Briefly say whether the shortlist was reused from cache or freshly retrieved
5. Note any skipped items, paywall limitations, or fetch failures
6. Preserve the user's trailing text requirements when they matter for later cache-fit decisions

## Error Handling

- Follow [search_guide.md](references/search_guide.md) for retrieval-related failures
- If the user asks for Chinese support, add Chinese notes or key points as an extra section after the English summary
