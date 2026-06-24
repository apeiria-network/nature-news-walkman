# Nature News Walkman Web Fetch Guide

This guide describes how `nature-news-walkman` should discover, fetch, filter, and prepare recent Nature NEWS articles before the audio step.

## Scope

Use this guide for the web-facing half of the workflow:
- Python environment bootstrap
- RSS retrieval
- URL shortlist preparation
- article fetching
- NEWS-only filtering
- optional cookie-file support
- summary-stage reading flow before audio selection

The user-facing command and interaction contract belong in [SKILL.md](../SKILL.md).

## Environment Setup

Before running the helper scripts for the first time, prepare the local Python environment:

```sh
bash scripts/venv_install.sh
```

This installs the required dependencies into `scripts/.venv`.

## Storage Convention

Helper scripts write into `<your workspace>/nature-news-walkman/`.
Here `<your workspace>` means the current working directory from which the scripts are run.

Typical subdirectories:
- `<your workspace>/nature-news-walkman/temp/`
- `<your workspace>/nature-news-walkman/audio/`

## Retrieval Workflow

### 1. Fetch the current RSS feed

Run:

```sh
python scripts/rss_fetch.py
```

This should:
- download `http://feeds.nature.com/nature/rss/current`
- save the raw RSS text as `NatureRSS.txt`
- extract candidate article URLs
- save those URLs to `nature_article_urls.txt`

### 2. Fetch article pages

Run:

```sh
python scripts/fetch_nature_article.py --url-file <your workspace>/nature-news-walkman/temp/nature_article_urls.txt
```

This script should:
- read article URLs from a file or accept a single `--url`
- fetch each page
- keep only pages that contain the `NEWS` marker
- save structured JSON article results

### 3. Respect fetch pacing

When the input contains multiple URLs:
- wait 5-10 seconds between article requests
- do not remove that delay during normal use
- use the `--limit` argument to cap how many URLs are processed in one run

Default behavior:
- `--limit 20`

Example:

```sh
python scripts/fetch_nature_article.py --url-file <your workspace>/nature-news-walkman/temp/nature_article_urls.txt --limit 5
```

## NEWS-Only Filtering Rule

An article is eligible only when the fetched HTML contains the Nature article-category marker for `NEWS`.

Non-NEWS pages must be skipped.

The fetch script should print skip messages such as:

```text
Skipping non-NEWS article: https://www.nature.com/articles/...
```

## Public vs Cookie-Assisted Fetching

### Default mode

By default, `fetch_nature_article.py` reads only the publicly visible article content.

### Optional cookie-file mode

If the user provides a local cookie file, the script may use it to request more complete article text.

Example:

```sh
python scripts/fetch_nature_article.py \
  --url https://www.nature.com/articles/d41586-026-01903-z \
  --cookie-file <your workspace>/nature-news-walkman/temp/cookie.txt
```

Rules:
- the user must provide their own cookie file
- the cookie file is local-only and should never be committed to git
- if the cookie file is missing or invalid, the script should either fail clearly or fall back to public-only behavior, depending on the current command path

## Article Output Schema

`fetch_nature_article.py` should produce a JSON list of article objects.

Each article must include:
- `title`
- `link`
- `date`
- `sub_title`
- `author`
- `full_text`
- `reference_list`

## Summary-Stage Reading Workflow

Before generating any audio, run:

```sh
python scripts/news_read.py
```

This should print structured text for up to 10 articles, ordered newest-first.

The model should then:
1. read the printed article list
2. summarize the shortlist in English
3. present numbered article options to the user
4. wait for the user's numeric selection

Do not generate audio before the user selects article numbers.

## Error Handling

- RSS fetch failure: report the failure and stop
- article fetch timeout: report the failure and continue when possible
- no NEWS articles found: report that no valid NEWS pages were available
- Unicode output issues: always print UTF-8-safe output from the scripts
- invalid cookie file path: report the missing file clearly

## Representative Commands

```sh
bash scripts/venv_install.sh
python scripts/rss_fetch.py
python scripts/fetch_nature_article.py --url-file <your workspace>/nature-news-walkman/temp/nature_article_urls.txt
python scripts/fetch_nature_article.py --url https://www.nature.com/articles/d41586-026-01923-9
python scripts/fetch_nature_article.py --url https://www.nature.com/articles/d41586-026-01903-z --cookie-file <your workspace>/nature-news-walkman/temp/cookie.txt
python scripts/news_read.py
```
