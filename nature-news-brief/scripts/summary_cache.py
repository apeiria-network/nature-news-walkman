#!/usr/bin/env python3
"""Cache helpers for Nature news shortlist batches."""

import json
from pathlib import Path


DEFAULT_OUTPUT_SUBDIR = Path('.claude/nature-news-walkman')


def resolve_default_output_dir() -> str:
    """Return the default writable project storage directory, creating it if needed."""
    project_root = Path(__file__).resolve().parents[2]
    candidate = project_root / DEFAULT_OUTPUT_SUBDIR
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        test_file = candidate / '.write_test.tmp'
        test_file.write_text('ok', encoding='utf-8')
        test_file.unlink()
        return str(candidate)
    except OSError:
        candidate.mkdir(parents=True, exist_ok=True)
        return str(candidate)


CACHE_FILENAME = 'Nature_LatestBatch_Cache.json'
REQUIRED_ARTICLE_FIELDS = ('title', 'date', 'summary', 'url')


def get_summary_cache_path(output_dir: str | None = None) -> Path:
    """Return the canonical cache path for the latest shortlist batch."""
    return Path(output_dir or resolve_default_output_dir()) / CACHE_FILENAME


def load_summary_cache(output_dir: str | None = None) -> dict | None:
    """Load the structured shortlist cache, returning None on read/parse failure."""
    cache_path = get_summary_cache_path(output_dir)
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    articles = data.get('articles')
    if not isinstance(articles, list):
        return None

    normalized_articles = []
    for article in articles:
        if not isinstance(article, dict):
            continue
        normalized_article = dict(article)
        missing_required = [field for field in REQUIRED_ARTICLE_FIELDS if not str(normalized_article.get(field, '')).strip()]
        if missing_required:
            continue
        normalized_articles.append(normalized_article)

    data['articles'] = normalized_articles
    data.setdefault('generated_at', None)
    data.setdefault('listing_url', 'https://www.nature.com/news')
    data['article_count'] = len(normalized_articles)
    data.setdefault('user_requirements', '')
    return data


def save_summary_cache(batch: dict, output_dir: str | None = None) -> str | None:
    """Save the structured shortlist cache and return the saved path on success."""
    if not isinstance(batch, dict):
        return None
    articles = batch.get('articles')
    if not isinstance(articles, list):
        return None

    normalized_articles = []
    for article in articles:
        if not isinstance(article, dict):
            continue
        normalized_article = dict(article)
        missing_required = [field for field in REQUIRED_ARTICLE_FIELDS if not str(normalized_article.get(field, '')).strip()]
        if missing_required:
            continue
        normalized_articles.append(normalized_article)

    if not normalized_articles:
        return None

    normalized = dict(batch)
    normalized['articles'] = normalized_articles
    normalized.setdefault('generated_at', None)
    normalized.setdefault('listing_url', 'https://www.nature.com/news')
    normalized.setdefault('user_requirements', '')
    normalized['article_count'] = len(normalized_articles)
    cache_path = get_summary_cache_path(output_dir)
    print(f"Using storage [project-claude-dir]: {cache_path}")
    try:
        cache_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding='utf-8')
    except OSError:
        return None
    return str(cache_path)
