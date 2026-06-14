# Nature News Sound Retrieval Guide

This document describes how `nature-news-sound` should retrieve, rank, cache, and reuse a shortlist of recent Nature news.

## Scope

Use this guide when `nature-news-sound` needs to prepare a shortlist of recent Nature news summaries for the user.

The skill-level output behavior belongs in [SKILL.md](../SKILL.md). This file covers retrieval, shortlist generation, cache handling, reuse decisions, and the rule that full original English text and audio are only provided after the user selects shortlist entries.

## Retrieval Workflow

1. Before searching, check whether an existing shortlist cache is available.
2. Compare that cache against the user's current request, including topic, style, freshness, and overall fit.
3. If the cache is still a good match and the user did not clearly ask for a refresh or a different batch, reuse it.
4. Otherwise, use **WebSearch** and/or **WebFetch** to identify the latest Nature news from `https://www.nature.com/news`.
5. Build a shortlist of the **top 10 news items** based primarily on **news-page heat, prominence, or apparent readership / browse visibility signals**.
6. If the user gives extra requirements, combine those requirements with the ranking judgment instead of using popularity alone.
7. For each shortlisted news item, record structured summary-stage information such as rank, title, URL, author (if available), date, short description, and summary.
8. Save that structured shortlist as the latest cache batch.
9. If a summary-stage fetch fails, retry once. If it still fails, skip that news item and continue to the next most suitable candidate.

## Ranking Rules

When selecting the top 10 news items, prioritize:
- news-page prominence on Nature news pages
- apparent heat / browse visibility / editorial highlighting
- recency
- relevance to any trailing user requirements
- availability of usable English source text

If the user gives a topic or style preference, balance that preference with the top-news ranking instead of ignoring one side entirely.

## Cache Management

Use `Nature_LatestBatch_Cache.json` as the structured cache for the latest shortlist batch.
The default cache storage directory is `.claude/nature-news-walkman/` under the project root.
Before saving the cache, the workflow should tell the user which storage path will be used.

The cache should store:
- batch timestamp
- listing URL
- trailing user requirements when relevant
- news count
- a top-10 news list

Each cached news entry must include:
- `title`
- `date`
- `summary`
- `url`

Each cached news entry may also include optional supporting fields such as:
- `author`
- `description`
- optional Chinese summary / notes
- optional later enrichment such as full text or audio path

Cache helper responsibilities:
- [scripts/summary_cache.py](../scripts/summary_cache.py) only reads and writes the structured cache
- invalid news entries should be filtered out if they do not contain the required `title`, `date`, `summary`, and `url` fields
- the cache helper must not decide whether a batch should be reused or refreshed

## Reuse Rules

When a cache is available:
- the **agent** decides whether to reuse the latest shortlist batch instead of searching again
- first compare the cached batch with the user's current request and whether the user clearly wants a refresh, a new topic, or a different batch
- reuse the cache only when it is still a good fit for the current request
- if the cache is a poor fit, stale for the task, or the user explicitly asks for fresh results, do a fresh retrieval instead
- if cache read fails, ignore the cache and do a fresh retrieval
- if cache write fails, continue the response, but later reuse may not be available

## Fetched Content Expectations

For each shortlisted news page:
- at summary stage, collect enough information to generate a useful shortlist preview
- prefer freely visible English source text for summaries
- keep metadata when available, including title, URL, author, and date
- if a page is partially paywalled, extract all freely visible text and keep a note about the limitation

For selected news in later steps:
- fetch or reuse the **full original English text** only after the user selects one or more shortlist entries
- generate audio only for the selected news after the English text is available

## Result Presentation Notes

When presenting shortlist results:
- briefly mention whether the shortlist was freshly fetched or reused from cache
- note any skipped news items
- note any paywall limitations
- note any fetch failures
- present the shortlist first, then ask the user to choose news numbers before providing any full text or audio

Detailed final formatting and delivery behavior should be handled by [SKILL.md](../SKILL.md).

## Error Handling

- **WebSearch or WebFetch fails for a candidate page**: retry once. If it still fails, skip that item and inform the user.
- **Cache read fails**: ignore the cache and do a fresh retrieval.
- **Cache write fails**: continue the response, but later reuse may not be available.
- **Paywalled content**: extract all freely visible text. Add a note for that news item.
- **Empty news text**: skip it and fetch the next most relevant Nature news item.

## Related Files

- `Nature_LatestBatch_Cache.json`: structured cache of the latest top-10 Nature news shortlist
- [scripts/summary_cache.py](../scripts/summary_cache.py): cache read/write helpers
- [TTS_guide.md](../references/TTS_guide.md): TTS guidance for selected news audio
