#!/usr/bin/env python3
"""
Generate English TTS audio for selected Nature news articles.

Usage:
    python scripts/nature_news_sound.py 1 2 3
    python scripts/nature_news_sound.py 1 --engine edge-tts
    python scripts/nature_news_sound.py 1 2 --input .claude/nature-news-walkman/data/nature_articles.json

Indices correspond to the article numbers printed by news_read.py (1-based, newest first).

Outputs mp3 files to: .claude/nature-news-walkman/audio/
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_INPUT_PATH = Path('.claude/nature-news-walkman/data/nature_articles.json')
DEFAULT_AUDIO_DIR = Path('.claude/nature-news-walkman/audio')
MAX_ARTICLES = 10
EDGE_TTS_VOICES = {
    'en': 'en-US-AvaNeural',
    'en-US': 'en-US-AvaNeural',
    'en-GB': 'en-GB-SoniaNeural',
    'zh-CN': 'zh-CN-XiaoxiaoNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
}


# ─── helpers ──────────────────────────────────────────────────────────────────

def get_venv_python() -> str:
    scripts_dir = Path(__file__).resolve().parent
    venv_dir = scripts_dir / '.venv'
    candidates = [
        venv_dir / 'Scripts' / 'python.exe',
        venv_dir / 'bin' / 'python',
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise RuntimeError(
        f'Virtual environment not found at {venv_dir}. '
        'Run: bash scripts/venv_install.sh'
    )


def parse_sort_key(date_value: str) -> tuple[int, str]:
    value = (date_value or '').strip()
    if not value:
        return (0, '')
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'):
        try:
            return (1, datetime.strptime(value, fmt).isoformat())
        except ValueError:
            continue
    return (0, value)


def load_sorted_articles(input_path: Path) -> list[dict]:
    data = json.loads(input_path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('Input JSON must be a list of article objects.')
    articles = [a for a in data if isinstance(a, dict) and a.get('title') and a.get('link')]
    articles.sort(key=lambda a: parse_sort_key(a.get('date', '')), reverse=True)
    return articles[:MAX_ARTICLES]


def clean_text_for_tts(text: str) -> str:
    text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'Credit:.*', '', text)
    text = re.sub(r'!\[(.*?)\]\(.*?\)', '', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*?doi:.*', '', text)
    text = re.sub(r'\*?Source:.*', '', text)
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def safe_filename(title: str, index: int) -> str:
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug).strip('-')[:60]
    return f'{index:03d}_{slug}.mp3'


# ─── TTS engines ──────────────────────────────────────────────────────────────

def generate_gtts(text: str, output_path: str, lang: str, python_path: str) -> bool:
    script = (
        "import sys; from gtts import gTTS; "
        "gTTS(text=sys.argv[1], lang=sys.argv[2], slow=False).save(sys.argv[3])"
    )
    result = subprocess.run(
        [python_path, '-c', script, text, lang, output_path],
        check=False, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True
    print(f'  gTTS error: {result.stderr.strip() or result.stdout.strip()}', file=sys.stderr)
    return False


def generate_edge_tts(text: str, output_path: str, lang: str, python_path: str) -> bool:
    voice = EDGE_TTS_VOICES.get(lang, EDGE_TTS_VOICES['en'])
    script = (
        "import asyncio, sys, edge_tts\n"
        "async def main():\n"
        "    await edge_tts.Communicate(sys.argv[1], sys.argv[2]).save(sys.argv[3])\n"
        "asyncio.run(main())"
    )
    result = subprocess.run(
        [python_path, '-c', script, text, voice, output_path],
        check=False, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True
    print(f'  edge-tts error: {result.stderr.strip() or result.stdout.strip()}', file=sys.stderr)
    return False


def generate_audio(text: str, output_path: str, lang: str, engine: str, python_path: str) -> tuple[bool, str]:
    cleaned = clean_text_for_tts(text)

    if engine == 'gtts':
        ok = generate_gtts(cleaned, output_path, lang, python_path)
        return (ok, 'gTTS' if ok else '')

    if engine == 'edge-tts':
        ok = generate_edge_tts(cleaned, output_path, lang, python_path)
        return (ok, 'edge-tts' if ok else '')

    # auto: gTTS first, edge-tts fallback
    print('  Trying gTTS...', end=' ', flush=True)
    ok = generate_gtts(cleaned, output_path, lang, python_path)
    if ok:
        print('OK')
        return (True, 'gTTS')
    print('failed, trying edge-tts...', end=' ', flush=True)
    ok = generate_edge_tts(cleaned, output_path, lang, python_path)
    if ok:
        print('OK')
        return (True, 'edge-tts')
    print('ERROR: both engines failed.', file=sys.stderr)
    return (False, '')


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate TTS audio for selected Nature news articles.'
    )
    parser.add_argument(
        'indices', nargs='+', type=int,
        help='1-based article indices from news_read.py output (e.g. 1 2 3)',
    )
    parser.add_argument(
        '--input', default=str(DEFAULT_INPUT_PATH),
        help='Path to fetched article JSON',
    )
    parser.add_argument(
        '--output-dir', default=str(DEFAULT_AUDIO_DIR),
        help='Directory to save mp3 files',
    )
    parser.add_argument(
        '--engine', default='auto', choices=['auto', 'gtts', 'edge-tts'],
        help='TTS engine (default: auto, gTTS first then edge-tts fallback)',
    )
    parser.add_argument(
        '--lang', default='en',
        help='Language code (default: en)',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f'Input file not found: {input_path}', file=sys.stderr)
        return 1

    try:
        python_path = get_venv_python()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        articles = load_sorted_articles(input_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not articles:
        print('No articles found in input file.', file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for idx in args.indices:
        if idx < 1 or idx > len(articles):
            print(f'Index {idx} out of range (1–{len(articles)}), skipping.', file=sys.stderr)
            continue

        article = articles[idx - 1]
        title = article.get('title', f'Article {idx}')
        body = (article.get('full_text') or '').strip()
        if not body:
            print(f'[{idx}] {title}: no body text, skipping.', file=sys.stderr)
            continue

        filename = safe_filename(title, idx)
        output_path = str(output_dir / filename)

        print(f'[{idx}] {title}')
        success, engine_used = generate_audio(body, output_path, args.lang, args.engine, python_path)

        if success:
            print(f'  Saved: {output_path}')
            results.append({'index': idx, 'title': title, 'audio': output_path, 'engine': engine_used})
        else:
            print(f'  Failed to generate audio for article {idx}.', file=sys.stderr)

    if not results:
        print('No audio files were generated.', file=sys.stderr)
        return 1

    print(f'\nDone. {len(results)} file(s) generated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
