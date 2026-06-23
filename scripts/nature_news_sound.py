#!/usr/bin/env python3
"""
Generate English TTS audio for selected Nature news articles.

Usage:
    python scripts/nature_news_sound.py 1 2 3
    python scripts/nature_news_sound.py 1 --engine edge-tts
    python scripts/nature_news_sound.py 1 --speed 0.8
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


def speed_to_edge_rate(speed: float | None) -> str | None:
    if speed is None or abs(speed - 1.0) < 1e-9:
        return None
    percent = round((speed - 1.0) * 100)
    sign = '+' if percent > 0 else ''
    return f'{sign}{percent}%'


def describe_speed(speed: float | None) -> str:
    if speed is None:
        return 'default speed'
    return f'{speed:g}x speed'


def safe_filename(title: str, index: int) -> str:
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug).strip('-')[:60]
    return f'{index:03d}_{slug}.mp3'


# ─── TTS engines ──────────────────────────────────────────────────────────────


def generate_gtts(text: str, output_path: str, lang: str, python_path: str, slow: bool = False) -> bool:
    script = (
        "import sys; from gtts import gTTS; "
        "gTTS(text=sys.argv[1], lang=sys.argv[2], slow=(sys.argv[4]=='1')).save(sys.argv[3])"
    )
    result = subprocess.run(
        [python_path, '-c', script, text, lang, output_path, '1' if slow else '0'],
        check=False, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True
    print(f'  gTTS error: {result.stderr.strip() or result.stdout.strip()}', file=sys.stderr)
    return False


def generate_edge_tts(text: str, output_path: str, lang: str, python_path: str, rate: str | None = None) -> bool:
    voice = EDGE_TTS_VOICES.get(lang, EDGE_TTS_VOICES['en'])
    if rate is None:
        script = (
            "import asyncio, sys, edge_tts\n"
            "async def main():\n"
            "    await edge_tts.Communicate(sys.argv[1], sys.argv[2]).save(sys.argv[3])\n"
            "asyncio.run(main())"
        )
        command = [python_path, '-c', script, text, voice, output_path]
    else:
        script = (
            "import asyncio, sys, edge_tts\n"
            "async def main():\n"
            "    await edge_tts.Communicate(sys.argv[1], sys.argv[2], rate=sys.argv[4]).save(sys.argv[3])\n"
            "asyncio.run(main())"
        )
        command = [python_path, '-c', script, text, voice, output_path, rate]
    result = subprocess.run(
        command,
        check=False, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True
    print(f'  edge-tts error: {result.stderr.strip() or result.stdout.strip()}', file=sys.stderr)
    return False


def generate_audio(text: str, output_path: str, lang: str, engine: str, python_path: str, speed: float | None) -> tuple[bool, str]:
    cleaned = clean_text_for_tts(text)
    edge_rate = speed_to_edge_rate(speed)
    gtts_slow = speed is not None and speed < 1.0
    gtts_fast_unsupported = speed is not None and speed > 1.0
    speed_desc = describe_speed(speed)

    if engine == 'gtts':
        if gtts_slow:
            print(f'  gTTS only supports slow/default speed; approximating {speed_desc} with slow=True.')
        elif gtts_fast_unsupported:
            print(f'  gTTS does not support accelerated speech; requested {speed_desc}, using default speed.')
        ok = generate_gtts(cleaned, output_path, lang, python_path, slow=gtts_slow)
        return (ok, 'gTTS' if ok else '')

    if engine == 'edge-tts':
        ok = generate_edge_tts(cleaned, output_path, lang, python_path, rate=edge_rate)
        return (ok, 'edge-tts' if ok else '')

    # auto: edge-tts first, gTTS fallback
    if edge_rate is None:
        print('  Trying edge-tts at default speed...', end=' ', flush=True)
    else:
        print(f'  Trying edge-tts at {speed_desc} (rate {edge_rate})...', end=' ', flush=True)
    ok = generate_edge_tts(cleaned, output_path, lang, python_path, rate=edge_rate)
    if ok:
        print('OK')
        return (True, 'edge-tts')
    print('failed, trying gTTS...', end=' ', flush=True)
    if gtts_slow:
        print(f'\n  gTTS only supports slow/default speed; approximating {speed_desc} with slow=True.')
    elif gtts_fast_unsupported:
        print(f'\n  gTTS does not support accelerated speech; requested {speed_desc}, using default speed.')
    ok = generate_gtts(cleaned, output_path, lang, python_path, slow=gtts_slow)
    if ok:
        print('OK')
        return (True, 'gTTS')
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
        help='TTS engine (default: auto, edge-tts first then gTTS fallback)',
    )
    parser.add_argument(
        '--lang', default='en',
        help='Language code (default: en)',
    )
    parser.add_argument(
        '--speed', type=float, default=None,
        help='Speech speed multiplier (e.g. 0.8, 1.0, 1.25). Omit to use the engine default speed.',
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
        success, engine_used = generate_audio(body, output_path, args.lang, args.engine, python_path, args.speed)

        if success:
            speed_label = describe_speed(args.speed)
            print(f'  Saved: {output_path} ({engine_used}, {speed_label})')
            results.append({'index': idx, 'title': title, 'audio': output_path, 'engine': engine_used, 'speed': args.speed})
        else:
            print(f'  Failed to generate audio for article {idx}.', file=sys.stderr)

    if not results:
        print('No audio files were generated.', file=sys.stderr)
        return 1

    print(f'\nDone. {len(results)} file(s) generated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
