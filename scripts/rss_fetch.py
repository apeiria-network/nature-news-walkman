#!/usr/bin/env python3
"""Fetch the current Nature RSS feed and extract latest article URLs."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_RSS_URL = 'http://feeds.nature.com/nature/rss/current'
DEFAULT_OUTPUT_DIR = Path('.claude/nature-news-walkman/tmp')
DEFAULT_RSS_PATH = DEFAULT_OUTPUT_DIR / 'NatureRSS.txt'
DEFAULT_URL_PATH = DEFAULT_OUTPUT_DIR / 'nature_article_urls.txt'
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/137.0.0.0 Safari/537.36'
)
ARTICLE_URL_RE = re.compile(r'^https://www\.nature\.com/articles/d[\w\-]+$')


def fetch_rss_text(rss_url: str, timeout: float) -> str:
    request = Request(rss_url, headers={'User-Agent': USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='replace')
    except HTTPError as exc:
        raise RuntimeError(f'HTTP error {exc.code} while fetching RSS: {rss_url}') from exc
    except URLError as exc:
        raise RuntimeError(f'Network error while fetching RSS: {exc.reason}') from exc


def extract_urls(rss_text: str) -> list[str]:
    seen = set()
    urls = []
    root = ET.fromstring(rss_text)

    for element in root.iter():
        for value in element.attrib.values():
            value = value.strip()
            if ARTICLE_URL_RE.match(value) and value not in seen:
                seen.add(value)
                urls.append(value)

        text = (element.text or '').strip()
        if ARTICLE_URL_RE.match(text) and text not in seen:
            seen.add(text)
            urls.append(text)

    return urls


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Fetch the current Nature RSS feed and save article URLs.')
    parser.add_argument('--rss-url', default=DEFAULT_RSS_URL, help='RSS feed URL')
    parser.add_argument('--rss-path', default=str(DEFAULT_RSS_PATH), help='Path to save RSS text')
    parser.add_argument('--url-path', default=str(DEFAULT_URL_PATH), help='Path to save extracted article URLs')
    parser.add_argument('--limit', type=int, default=0, help='Maximum number of URLs to keep (0 = all)')
    parser.add_argument('--timeout', type=float, default=20.0, help='HTTP timeout in seconds')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rss_path = Path(args.rss_path)
    url_path = Path(args.url_path)

    try:
        rss_text = fetch_rss_text(args.rss_url, timeout=args.timeout)
        rss_path.parent.mkdir(parents=True, exist_ok=True)
        rss_path.write_text(rss_text, encoding='utf-8')
        urls = extract_urls(rss_text)
    except (RuntimeError, ET.ParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.limit > 0:
        urls = urls[:args.limit]

    write_lines(url_path, urls)
    print(f'RSS saved to: {rss_path}')
    print(f'URL list saved to: {url_path}')
    print(f'Article count: {len(urls)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
