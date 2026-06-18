#!/usr/bin/env python3
"""Fetch a Nature article page and print structured JSON."""

import argparse
import json
import re
import sys
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)
ARTICLE_ID_RE = re.compile(r"(d41586-[0-9]{3}-[0-9]{5}-[a-z0-9]|s41586-[0-9]{3}-[0-9]{5}-[a-z0-9])")
META_RE = re.compile(r'<meta\s+[^>]*(?:name|property)=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\']|<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']([^"\']+)["\']', re.I)
JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
CANONICAL_RE = re.compile(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.I)
WHITESPACE_RE = re.compile(r'\s+')
NOISE_HINTS = (
    'related', 'newsletter', 'subscribe', 'citation', 'reference', 'footer',
    'tab-panel', 'accordion', 'metrics', 'figure', 'figcaption', 'nav', 'toolbar',
    'share', 'advert', 'banner', 'cookie', 'login', 'signin', 'author-information'
)


def normalize_input(value):
    value = value.strip()
    match = ARTICLE_ID_RE.search(value)
    if not match:
        raise ValueError('Input must be a Nature article URL or article id.')
    article_id = match.group(1)
    return article_id, f'https://www.nature.com/articles/{article_id}'


def fetch_html(url, timeout):
    request = Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            html = response.read().decode('utf-8', errors='replace')
    except HTTPError as exc:
        raise RuntimeError(f'HTTP error {exc.code} while fetching {url}') from exc
    except URLError as exc:
        raise RuntimeError(f'Network error while fetching {url}: {exc.reason}') from exc
    return final_url, html


def extract_article_segment(html):
    start_marker = '<article class="article-item article-item--open"'
    start = html.find(start_marker)
    if start == -1:
        start = html.find('<article')
    if start == -1:
        return html

    end_markers = (
        '<h2 class="c-article-section__title js-section-title">Access options</h2>',
        '<h2 class="c-article-section__title js-section-title" id="access-options">Access options</h2>',
        '<div id="references"',
    )
    end = -1
    for marker in end_markers:
        marker_index = html.find(marker, start)
        if marker_index != -1 and (end == -1 or marker_index < end):
            end = marker_index
    if end == -1:
        end = len(html)
    return html[start:end]


def extract_meta_map(html):
    meta = {}
    for match in META_RE.finditer(html):
        if match.group(1) and match.group(2) is not None:
            key, value = match.group(1), match.group(2)
        else:
            key, value = match.group(4), match.group(3)
        meta[key.strip().lower()] = unescape(value.strip())
    return meta


def extract_json_ld_objects(html):
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
            if isinstance(parsed.get('@graph'), list):
                objects.extend(item for item in parsed['@graph'] if isinstance(item, dict))
            else:
                objects.append(parsed)
    return objects


def extract_canonical_link(html, fallback_url):
    match = CANONICAL_RE.search(html)
    if match:
        return unescape(match.group(1).strip())
    return fallback_url


def first_nonempty(*values):
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


def extract_from_json_ld(objects, field_names):
    for obj in objects:
        for field_name in field_names:
            value = obj.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ''



def clean_text(text):
    text = unescape(text)
    text = text.replace('\xa0', ' ')
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = text.replace('’', "'")
    text = text.replace('‘', "'")
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('…', '...')
    text = text.encode('ascii', 'replace').decode('ascii')
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text, flags=re.I | re.S)
    text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    text = re.sub(r'(?<=\w)\s+(\d{1,3})\s*(?=[\.,;:!?]|$)', '', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = WHITESPACE_RE.sub(' ', text)
    text = re.sub(r'\s+([\.,;:!?])', r'\1', text)
    return text.strip()


def dedupe_repeated_sentence(text):
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


def dedupe_summary_prefix(full_text, summary):
    if not summary:
        return full_text
    summary_norm = clean_text(summary)
    full_norm = clean_text(full_text)
    if full_norm.lower().startswith(summary_norm.lower()):
        trimmed = full_norm[len(summary_norm):].lstrip(' .:\n')
        return trimmed or full_norm
    return full_text


def extract_full_text(html):
    segment = extract_article_segment(html)
    paragraph_matches = re.findall(r'<p[^>]*>(.*?)</p>', segment, re.I | re.S)
    heading_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', segment, re.I | re.S)

    blocks = []
    seen = set()
    noise_prefixes = (
        'access nature and',
        'get nature+',
        'subscription info',
        'we have a dedicated website',
        'rent or buy this article',
        'prices vary by article type',
        'from $',
        'to $',
        'prices may be subject',
        'sign up to nature briefing',
        'sign up for the nature briefing',
        'doi:',
        'bluesky facebook linkedin reddit whatsapp x',
        'search author on:',
        'enjoying our latest content?',
        'log in or create an account to continue',
    )

    for raw in heading_matches + paragraph_matches:
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = clean_text(text)
        lower = text.lower()
        if not text or len(text) < 25:
            continue
        if any(lower.startswith(prefix) for prefix in noise_prefixes):
            continue
        if lower.endswith('is a reporter for nature in sydney, australia.'):
            continue
        if 'credit:' in lower and len(text) < 260:
            continue
        if text in {'Access options'}:
            continue
        if lower in seen:
            continue
        seen.add(lower)
        blocks.append(text)

    return '\n\n'.join(blocks)


def build_result(article_id, link, html):
    meta = extract_meta_map(html)
    json_ld = extract_json_ld_objects(html)
    title = first_nonempty(
        meta.get('og:title'),
        meta.get('dc.title'),
        meta.get('citation_title'),
        extract_from_json_ld(json_ld, ('headline', 'name')),
    )
    date = first_nonempty(
        meta.get('article:published_time'),
        meta.get('dc.date'),
        meta.get('citation_publication_date'),
        extract_from_json_ld(json_ld, ('datePublished', 'dateCreated')),
    )
    summary = first_nonempty(
        meta.get('description'),
        meta.get('og:description'),
        meta.get('dc.description'),
        extract_from_json_ld(json_ld, ('description',)),
    )
    summary = dedupe_repeated_sentence(clean_text(summary))
    full_text = extract_full_text(html)
    if not summary and full_text:
        summary = full_text.split('\n\n', 1)[0]
    full_text = dedupe_summary_prefix(full_text, summary)
    result = {
        'id': article_id,
        'title': clean_text(title),
        'link': link,
        'date': clean_text(date),
        'summary': clean_text(summary),
        'full_text': full_text.strip(),
    }
    if not result['title']:
        raise RuntimeError('Failed to extract article title.')
    if not result['full_text']:
        raise RuntimeError('Failed to extract article body text.')
    return result


def parse_args():
    parser = argparse.ArgumentParser(description='Fetch a Nature article page and print structured JSON.')
    parser.add_argument('article', help='Nature article URL or article id')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    parser.add_argument('--timeout', type=float, default=20.0, help='HTTP timeout in seconds (default: 20)')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        article_id, url = normalize_input(args.article)
        final_url, html = fetch_html(url, timeout=args.timeout)
        link = extract_canonical_link(html, final_url)
        result = build_result(article_id, link, html)
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())



