#!/usr/bin/env python3
"""Print Nature news articles as structured text for model consumption."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

DEFAULT_INPUT_PATH = Path('.claude/nature-news-walkman/data/nature_articles.json')
MAX_ARTICLES = 10


def parse_sort_key(date_value: str) -> tuple[int, str]:
    value = (date_value or '').strip()
    if not value:
        return (0, '')

    formats = (
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
    )
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return (1, parsed.isoformat())
        except ValueError:
            continue
    return (0, value)


def normalize_article(article: dict) -> dict:
    return {
        'title': (article.get('title') or '').strip(),
        'url': (article.get('link') or '').strip(),
        'author': (article.get('author') or '').strip(),
        'full_text': (article.get('full_text') or '').strip(),
        'date': (article.get('date') or '').strip(),
    }


def load_articles(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('Input JSON must be a list of article objects.')
    return [item for item in data if isinstance(item, dict)]


def build_articles(articles: list[dict]) -> list[dict]:
    normalized = [normalize_article(article) for article in articles]
    normalized = [article for article in normalized if article['title'] and article['url']]
    normalized.sort(key=lambda article: parse_sort_key(article['date']), reverse=True)
    return normalized[:MAX_ARTICLES]


def format_articles(articles: list[dict]) -> str:
    lines = [f'Total articles: {len(articles)}']
    for index, article in enumerate(articles, start=1):
        lines.extend([
            '',
            f'Article {index}',
            f'Title: {article["title"]}',
            f'URL: {article["url"]}',
            f'Author: {article["author"] or "Unknown"}',
            'Full_text:',
            article['full_text'] or '(empty)',
        ])
    return '\n'.join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Print Nature news articles as structured text for model consumption.')
    parser.add_argument('--input', default=str(DEFAULT_INPUT_PATH), help='Path to fetched article JSON')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        raise SystemExit(f'Input file not found: {input_path}')

    try:
        articles = load_articles(input_path)
        selected_articles = build_articles(articles)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(format_articles(selected_articles))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
