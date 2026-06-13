---
name: nature-news-text
description: Provide a full-text Nature news reading skill. Fetch or reuse the latest top Nature news shortlist, present summary previews first, then deliver the full original English text only for the article numbers the user selects. Use when the user wants full article text, English reading practice, or `/nature-news-text`.
agent_created: true
---

# Nature News Text

Provide a full-text Nature news reading experience built around a reusable top-10 shortlist.

## When to Use

- User wants the full original English text of recent Nature news
- User wants English reading practice with complete articles instead of summaries only
- User wants to preview a shortlist before choosing which article to read
- User uses `/nature-news-text`

## Command

### `/nature-news-text [user requirements]`
- First present the shared top-10 news shortlist as summaries
- Then output the **full original English text** only for the article(s) the user selects
- Do not replace the selected news text with a summary unless the user explicitly asks

## User Requirements After the Command

Any text after the command is part of the user's request and should be preserved.

Examples:
- `/nature-news-text cancer biology, keep terminology, also add Chinese key points`
- `/nature-news-text climate topic, keep the original wording`
- `/nature-news-text choose space-related news, suitable for reading practice`

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

## Interaction Flow for `text`

1. Retrieve or reuse the shared top-10 summary shortlist
2. Present the top-10 summary text to the user in ranking order
3. Ask the user to choose one or more article numbers, and wait until user provides an answer
4. Fetch or reuse the **full original English text** only for the selected article(s)
5. Output the selected full English text
6. If the user asks for Chinese support, add it after each selected English original text

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
```

## Present Results

1. Deliver the shortlist summary text directly in the conversation before article selection
2. After the user selects article numbers, deliver the selected full-text result directly in the conversation
3. Do not write the text result to a markdown file
4. Follow the shared retrieval guide for batch freshness, skipped items, paywall notes, and fetch-failure notes
5. Preserve the user's trailing text requirements for possible later mode switches

## Error Handling

- Follow the shared retrieval guide for retrieval-related failures
- If the user asks for both full text and extra annotations, keep the original English text as the primary output and place extra annotations after it
