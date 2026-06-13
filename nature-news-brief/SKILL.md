---
name: nature-news-brief
description: Provide a summary-first Nature news briefing skill. Fetch or reuse the latest top Nature news shortlist, then present up to 10 ranked English summaries with optional Chinese notes. Use when the user wants Nature news summaries, a short reading digest, or `/nature-news-brief`.
agent_created: true
---

# Nature News Brief

Provide a summary-first Nature news briefing experience built around a reusable top-10 shortlist.

## When to Use

- User asks for Nature news summaries or a short digest
- User wants brief English reading practice from recent Nature news
- User wants a ranked shortlist instead of full article text
- User uses `/nature-news-brief`

## Command

### `/nature-news-brief [user requirements]`
- Output summary-stage results for the shared shortlist
- Each summary should be about **75-100 words**
- The summary is generated from fetched English news text or other usable summary-stage source text

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-brief easier English, climate topic, scientific tone`
- `/nature-news-brief cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-brief choose space-related news, suitable for reading practice`

The command name controls the output mode. The trailing text controls customization.

## Shared Retrieval Reference

Use the shared retrieval logic in [search_guide.md](../references/search_guide.md).

That shared guide covers:
- Latest Nature news discovery
- Top-10 shortlist ranking rules
- Structured summary-cache management
- Retry behavior
- Cache reuse policy
- Shared notes for skipped items, paywalls, and fetch failures

## Output Rules for `brief`

For the shared top-10 shortlist:
- Output `News {N}: {English Title}`
- Include `Publication Date: {Date in English}` when available
- Include `Source: {URL}`
- Output one English summary of about **75-100 words** for each shortlisted item
- If the user asks for Chinese support, add Chinese notes or key points as an extra section
- Do not output the full English text unless the user explicitly asks

`brief` should both:
- save the structured top-10 summary shortlist to cache through the shared retrieval flow
- send the summary text of the shortlist directly to the user in the conversation

`brief` does not require a selection step by default. It is the summary-oriented view of the shared shortlist.

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
4. Follow the shared retrieval guide for batch freshness, skipped items, paywall notes, and fetch-failure notes
5. Preserve the user's trailing text requirements for possible later mode switches

## Error Handling

- Follow the shared retrieval guide for retrieval-related failures
- If the user asks for Chinese support, add Chinese notes or key points as an extra section after the English summary
