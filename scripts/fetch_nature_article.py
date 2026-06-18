#!/usr/bin/env python3
"""Fetch one or more Nature news articles and save structured JSON."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import random
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/137.0.0.0 Safari/537.36'
)
DEFAULT_OUTPUT_PATH = Path('.claude/nature-news-walkman/data/nature_articles.json')
DEFAULT_MIN_DELAY = 5.0
DEFAULT_MAX_DELAY = 10.0
ARTICLE_URL_RE = re.compile(r'https://www\.nature\.com/articles/d[\w\-]+')
JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
META_RE = re.compile(
    r'<meta\s+[^>]*(?:name|property)=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\']'
    r'|<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']([^"\']+)["\']',
    re.I,
)
CANONICAL_RE = re.compile(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.I)
REFERENCE_SECTION_RE = re.compile(r'<(section|div)[^>]+id=["\']references["\'][^>]*>(.*?)</\1>', re.I | re.S)
REF_ENTRY_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.I | re.S)
TAG_RE = re.compile(r'<[^>]+>')
WHITESPACE_RE = re.compile(r'\s+')
NEWS_MARKER_RE = re.compile(
    r'<li[^>]*data-test=["\']article-category["\'][^>]*>\s*<span[^>]*class=["\']c-article-identifiers__type["\'][^>]*>\s*NEWS\s*</span>',
    re.I | re.S,
)


class NatureBodyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.current_tag: str | None = None
        self.current_parts: list[str] = []
        self.capture_depth = 0
        self.ignore_stack: list[str] = []
        self.skip_block_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key: (value or '') for key, value in attrs}
        class_value = attrs_map.get('class', '')
        lower_class = class_value.lower()

        if self.skip_block_depth:
            if tag in {'div', 'article', 'figure'}:
                self.skip_block_depth += 1
            return

        if tag == 'sup':
            self.ignore_stack.append(tag)
            return

        if tag in {'figure', 'article', 'div'} and (
            'figure' in lower_class
            or 'recommended' in lower_class
            or 'app-access-wall' in lower_class
            or 'article-related' in lower_class
        ):
            self.skip_block_depth = 1
            return

        if tag in {'p', 'h2'}:
            self.current_tag = tag
            self.current_parts = []
            self.capture_depth = 1
            return

        if self.current_tag:
            self.capture_depth += 1
            if tag == 'br':
                self.current_parts.append(' ')

    def handle_endtag(self, tag: str) -> None:
        if self.skip_block_depth:
            if tag in {'div', 'article', 'figure'}:
                self.skip_block_depth -= 1
            return

        if self.ignore_stack and tag == self.ignore_stack[-1]:
            self.ignore_stack.pop()
            return

        if self.current_tag:
            if tag == self.current_tag:
                text = clean_text(''.join(self.current_parts))
                if text:
                    self.blocks.append(text)
                self.current_tag = None
                self.current_parts = []
                self.capture_depth = 0
                return

            if self.capture_depth > 0:
                self.capture_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.current_tag and not self.ignore_stack and not self.skip_block_depth:
            self.current_parts.append(data)


def clean_text(text: str) -> str:
    text = unescape(text)
    text = text.replace('\xa0', ' ')
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = text.replace('’', "'")
    text = text.replace('‘', "'")
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('…', '...')
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text, flags=re.I | re.S)
    text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    text = TAG_RE.sub(' ', text)
    text = WHITESPACE_RE.sub(' ', text)
    text = re.sub(r'\s+([\.,;:!?])', r'\1', text)
    return text.strip()


def dedupe_repeated_sentence(text: str) -> str:
    parts = [part.strip() for part in re.split(r'(?<=[.!?])\s+', text) if part.strip()]
    if len(parts) == 2 and parts[0].lower() == parts[1].lower():
        return parts[0]
    halfway = len(text) // 2
    if halfway and len(text) % 2 == 0:
        left = text[:halfway].strip()
        right = text[halfway:].strip()
        if left and left.lower() == right.lower():
            return left
    return text


def read_url_file(path: Path) -> list[str]:
    urls = []
    seen = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        value = line.strip()
        if value and value not in seen:
            seen.add(value)
            urls.append(value)
    return urls


def read_cookie_file(path: Path) -> str:
    return path.read_text(encoding='utf-8').strip()


def fetch_html(url: str, timeout: float, cookie: str = '') -> tuple[str, str]:
    headers = {'User-Agent': USER_AGENT}
    if cookie:
        headers['Cookie'] = cookie
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            html = response.read().decode('utf-8', errors='replace')
    except HTTPError as exc:
        raise RuntimeError(f'HTTP error {exc.code} while fetching {url}') from exc
    except URLError as exc:
        raise RuntimeError(f'Network error while fetching {url}: {exc.reason}') from exc
    return final_url, html


def extract_meta_map(html: str) -> dict[str, str]:
    meta = {}
    for match in META_RE.finditer(html):
        if match.group(1) and match.group(2) is not None:
            key, value = match.group(1), match.group(2)
        else:
            key, value = match.group(4), match.group(3)
        meta[key.strip().lower()] = unescape(value.strip())
    return meta


def extract_json_ld_objects(html: str) -> list[dict]:
    objects = []
    for raw in JSON_LD_RE.findall(html):
        text = raw.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            objects.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            graph = parsed.get('@graph')
            if isinstance(graph, list):
                objects.extend(item for item in graph if isinstance(item, dict))
            else:
                objects.append(parsed)
    return objects


def first_nonempty(*values: str) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


def extract_from_json_ld(objects: list[dict], *field_names: str) -> str:
    for obj in objects:
        for field_name in field_names:
            value = obj.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ''


def extract_author_from_json_ld(objects: list[dict]) -> str:
    for obj in objects:
        author = obj.get('author')
        if isinstance(author, dict):
            name = author.get('name')
            if isinstance(name, str) and name.strip():
                return name.strip()
        if isinstance(author, list):
            names = []
            for item in author:
                if isinstance(item, dict):
                    name = item.get('name')
                    if isinstance(name, str) and name.strip():
                        names.append(name.strip())
            if names:
                return ', '.join(names)
    return ''


def normalize_author(author: str) -> str:
    author = clean_text(author)
    if ',' in author:
        left, right = [part.strip() for part in author.split(',', 1)]
        if left and right:
            return f'{right} {left}'
    return author


def is_news_article(html: str) -> bool:
    return NEWS_MARKER_RE.search(html) is not None


def extract_canonical_link(html: str, fallback_url: str) -> str:
    match = CANONICAL_RE.search(html)
    if match:
        return unescape(match.group(1).strip())
    return fallback_url


def extract_balanced_block(html: str, start_marker: str, tag_name: str) -> str:
    start = html.find(start_marker)
    if start == -1:
        return ''

    open_pat = f'<{tag_name}'
    close_pat = f'</{tag_name}>'
    index = start
    depth = 0
    entered = False

    while index < len(html):
        next_open = html.find(open_pat, index)
        next_close = html.find(close_pat, index)
        if next_close == -1:
            return html[start:]

        if next_open != -1 and next_open < next_close:
            depth += 1
            entered = True
            index = next_open + len(open_pat)
            continue

        depth -= 1
        index = next_close + len(close_pat)
        if entered and depth == 0:
            return html[start:index]

    return html[start:]


def extract_article_segment(html: str) -> str:
    body = extract_balanced_block(html, '<div class="c-article-body main-content"', 'div')
    if not body:
        return ''

    teaser = extract_balanced_block(body, '<div class="article__teaser"', 'div')
    return teaser or body


def extract_full_text(html: str) -> str:
    segment = extract_article_segment(html)
    if not segment:
        return ''

    parser = NatureBodyParser()
    parser.feed(segment)

    blocks = []
    seen = set()
    noise_prefixes = (
        'access nature and',
        'get nature+',
        'subscription info',
        'we have a dedicated website',
        'rent or buy this article',
        'prices vary by article type',
        'prices may be subject',
        'from $',
        'to $',
        'sign up to nature briefing',
        'sign up for the nature briefing',
        'doi:',
        'bluesky facebook linkedin reddit whatsapp x',
        'search author on:',
        'log in or create an account to continue',
        'enjoying our latest content?',
        'continue with google',
        'continue with orcid',
    )

    for text in parser.blocks:
        lower = text.lower()
        if len(text) < 2:
            continue
        if any(lower.startswith(prefix) for prefix in noise_prefixes):
            continue
        if 'credit:' in lower and len(text) < 260:
            continue
        if lower.endswith('is a reporter for nature in sydney, australia.'):
            continue
        if lower.endswith('is a reporter for nature in london, uk.'):
            continue
        if lower in seen:
            continue
        if len(text) < 25 and text.lower() not in {'inconsistent rules', 'just chilling'}:
            continue
        seen.add(lower)
        blocks.append(text)

    return '\n\n'.join(blocks)


def extract_reference_list(html: str) -> list[str]:
    match = REFERENCE_SECTION_RE.search(html)
    if not match:
        return []
    references = []
    seen = set()
    for raw in REF_ENTRY_RE.findall(match.group(2)):
        text = clean_text(raw)
        if text and text not in seen:
            seen.add(text)
            references.append(text)
    return references


def build_article(url: str, timeout: float, cookie: str = '') -> dict:
    final_url, html = fetch_html(url, timeout=timeout, cookie=cookie)
    if not is_news_article(html):
        raise RuntimeError(f'Skipping non-NEWS article: {url}')

    meta = extract_meta_map(html)
    json_ld = extract_json_ld_objects(html)
    link = extract_canonical_link(html, final_url)
    title = first_nonempty(
        meta.get('og:title', ''),
        meta.get('dc.title', ''),
        meta.get('citation_title', ''),
        extract_from_json_ld(json_ld, 'headline', 'name'),
    )
    date = first_nonempty(
        meta.get('article:published_time', ''),
        meta.get('dc.date', ''),
        meta.get('citation_publication_date', ''),
        extract_from_json_ld(json_ld, 'datePublished', 'dateCreated'),
    )
    sub_title = dedupe_repeated_sentence(clean_text(first_nonempty(
        meta.get('description', ''),
        meta.get('og:description', ''),
        meta.get('dc.description', ''),
        extract_from_json_ld(json_ld, 'description'),
    )))
    author = normalize_author(first_nonempty(
        meta.get('citation_author', ''),
        meta.get('dc.creator', ''),
        extract_author_from_json_ld(json_ld),
    ))
    full_text = extract_full_text(html)
    if not title:
        raise RuntimeError(f'Failed to extract article title from {url}')
    if not full_text:
        raise RuntimeError(f'Failed to extract article body text from {url}')
    return {
        'title': clean_text(title),
        'link': link,
        'date': clean_text(date),
        'sub_title': clean_text(sub_title),
        'author': clean_text(author),
        'full_text': full_text.strip(),
        'reference_list': extract_reference_list(html),
    }


def sleep_between_requests() -> None:
    time.sleep(random.uniform(DEFAULT_MIN_DELAY, DEFAULT_MAX_DELAY))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Fetch Nature news articles and save structured JSON.')
    parser.add_argument('--url', help='Single Nature article URL')
    parser.add_argument('--url-file', help='Text file containing one Nature article URL per line')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT_PATH), help='Path to save structured JSON')
    parser.add_argument('--cookie-file', help='Path to a local file containing the Nature Cookie header value')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    parser.add_argument('--timeout', type=float, default=20.0, help='HTTP timeout in seconds')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.url and not args.url_file:
        print('Please provide --url or --url-file.', file=sys.stderr)
        return 1

    urls = []
    cookie = ''
    if args.cookie_file:
        cookie_file = Path(args.cookie_file)
        if not cookie_file.exists():
            print(f'Cookie file not found: {cookie_file}', file=sys.stderr)
            return 1
        cookie = read_cookie_file(cookie_file)

    if args.url:
        urls.append(args.url.strip())
    if args.url_file:
        url_file = Path(args.url_file)
        if not url_file.exists():
            print(f'URL file not found: {url_file}', file=sys.stderr)
            return 1
        urls.extend(read_url_file(url_file))

    deduped_urls = []
    seen = set()
    for url in urls:
        match = ARTICLE_URL_RE.search(url)
        if not match:
            print(f'Skipping unsupported URL: {url}', file=sys.stderr)
            continue
        normalized = match.group(0)
        if normalized not in seen:
            seen.add(normalized)
            deduped_urls.append(normalized)

    if not deduped_urls:
        print('No valid Nature news article URLs were provided.', file=sys.stderr)
        return 1

    articles = []
    for index, url in enumerate(deduped_urls):
        try:
            article = build_article(url, timeout=args.timeout, cookie=cookie)
            articles.append(article)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
        if index < len(deduped_urls) - 1:
            sleep_between_requests()

    if not articles:
        print('Failed to fetch any Nature news articles.', file=sys.stderr)
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if args.pretty else None
    output_path.write_text(json.dumps(articles, ensure_ascii=False, indent=indent), encoding='utf-8')
    print(json.dumps(articles, ensure_ascii=False, indent=indent))
    print(f'Saved {len(articles)} article(s) to: {output_path}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
