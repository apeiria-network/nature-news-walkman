# Shared Retrieval Guide

This document contains the shared retrieval logic for the three sibling Nature news skills: `/nature-news-brief`, `/nature-news-text`, and `/nature-news-sound`.

## Scope

Apply this guide across all 3 sibling skills:
- `/nature-news-brief`
- `/nature-news-text`
- `/nature-news-sound`

The skill-specific output behavior should be defined in each skill's own `SKILL.md`. This file covers the shared Nature news retrieval, shortlist generation, cache management, and reuse logic.

## Shared Retrieval Logic

Across all 3 sibling skills:

1. Use **WebSearch** and/or **WebFetch** to identify the latest Nature news from `https://www.nature.com/news`
2. Build a shortlist of the **top 10 news items** based primarily on **news-page heat, prominence, or apparent readership / browse visibility signals**
3. If the user gives extra requirements, combine those requirements with the ranking judgment instead of using popularity alone
4. For each shortlisted news item, record structured summary-stage information such as rank, title, URL, author (if available), date, short description, and summary
5. Save that structured shortlist as the latest shared cache batch
6. If a summary-stage fetch fails, retry once. If it still fails, skip that news item and continue to the next most suitable candidate

## Ranking Rules

When selecting the top 10 news items, prioritize:
- News-page prominence on Nature news pages
- Apparent heat / browse visibility / editorial highlighting
- Recency
- Relevance to any trailing user requirements
- Availability of usable English source text

If the user gives a topic or style preference, balance that preference with the top-news ranking instead of ignoring one side entirely.

## Shared Summary Cache Management

Use `Nature_LatestBatch_Cache.json` as a structured shortlist cache for the latest shared retrieval batch.

The cache should store:
- batch timestamp
- listing URL
- trailing user requirements when relevant
- article count
- a top-10 `articles` list

Each cached article entry must include:
- `title`
- `date`
- `summary`
- `url`

Each cached article entry may also include optional supporting fields such as:
- `author`
- `description`
- optional Chinese summary / notes
- optional later enrichment such as full text or audio path

Cache helper responsibilities:
- [scripts/summary_cache.py](../scripts/summary_cache.py) only reads and writes the structured cache
- Invalid article entries should be filtered out if they do not contain the required `title`, `date`, `summary`, and `url` fields
- The cache helper must not decide whether a batch should be reused or refreshed

## Cache Reuse Rules

When lightweight cache reuse is available:
- The **agent** decides whether to reuse the latest fetched **summary batch** instead of searching again
- Reuse is especially preferred when the user switches between `brief`, `text`, and `sound`
- If the user clearly asks to refresh, re-search, switch topic, or use a different batch, the agent should do a fresh retrieval instead
- Preserve the user's original trailing text requirements so later commands can reuse them when appropriate
- If cache read fails, ignore the cache and do a fresh retrieval
- If cache write fails, continue the response, but later command reuse may not be available

## Fetched Content Expectations

For each shortlisted news page:
- At summary stage, collect enough information to generate a useful shortlist preview
- Prefer freely visible English source text for summaries
- Keep metadata when available, including title, URL, author, and date
- If a page is partially paywalled, extract all freely visible text and keep a note about the limitation

For selected articles in later steps:
- `text` and `sound` modes may fetch or reuse the **full original English text** only after the user selects one or more shortlist entries

## Shared Result Presentation Notes

When presenting results for any command mode:
- Briefly mention whether the current shortlist batch was freshly fetched or reused from cache
- Note any skipped news items
- Note any paywall limitations
- Note any fetch failures

The detailed text formatting and delivery behavior should be handled by each skill's `SKILL.md`.

## Shared Error Handling

- **WebSearch or WebFetch fails for a candidate page**: Retry once. If it still fails, skip that item and inform the user.
- **Cache read fails**: Ignore the cache and do a fresh retrieval.
- **Cache write fails**: Continue the response, but later command reuse may not be available.
- **Paywalled content**: Extract all freely visible text. Add a note for that news item.
- **Empty news text**: Skip it and fetch the next most relevant Nature news item.

## Related Files

- `Nature_LatestBatch_Cache.json`: structured cache of the latest shared top-10 Nature news shortlist
- [scripts/summary_cache.py](../scripts/summary_cache.py): cache read/write helpers
- Command-specific guides should reference this shared retrieval guide instead of duplicating the retrieval and cache-management logic
