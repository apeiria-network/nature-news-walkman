#!/usr/bin/env python3
"""
Nature News Digest - TTS Helper

Usage:
    python3 nature_digest.py --output-dir D:/nature-news-digest-sounds --tts
    python3 nature_digest.py --output-dir D:/nature-news-digest-sounds --tts --tts-engine edge-tts

Outputs:
    - Nature_Article{N}_English.mp3   (English TTS audio per article, if --tts)

TTS runtime:
    - Reuse the skill-local .venv first
    - Create .venv under the skill root if needed
    - Install missing runtime dependencies only into that .venv

TTS Engines:
    - gTTS (default): Google TTS, requires internet access to Google servers
    - edge-tts (fallback): Microsoft Edge TTS, works in China without VPN
"""

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path

from local_venv import ensure_local_venv


DEFAULT_OUTPUT_DIRS = [
    Path('D:/nature-news-digest-sounds'),
    Path('C:/nature-news-digest-sounds'),
]


def resolve_default_output_dir() -> str:
    """Return the preferred writable output directory, creating it if needed."""
    for candidate in DEFAULT_OUTPUT_DIRS:
        drive_root = candidate.drive + '/'
        if candidate.drive and not Path(drive_root).exists():
            continue
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            test_file = candidate / '.write_test.tmp'
            test_file.write_text('ok', encoding='utf-8')
            test_file.unlink()
            return str(candidate)
        except OSError:
            continue
    fallback = DEFAULT_OUTPUT_DIRS[-1]
    fallback.mkdir(parents=True, exist_ok=True)
    return str(fallback)


def latest_batch_cache(data: dict | None = None, output_dir: str | None = None) -> dict | str | None:
    """Read or write the latest Nature news batch cache JSON."""
    cache_path = Path(output_dir or resolve_default_output_dir()) / 'Nature_LatestBatch_Cache.json'
    if data is None:
        if not cache_path.exists():
            return None
        return json.loads(cache_path.read_text(encoding='utf-8'))
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(cache_path)


def clean_text_for_tts(text: str) -> str:
    """Clean article text for TTS: remove markdown formatting, credit lines, etc."""
    # Remove markdown bold/italic
    text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
    # Remove markdown links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove credit lines
    text = re.sub(r'Credit:.*', '', text)
    # Remove image references
    text = re.sub(r'!\[(.*?)\]\(.*?\)', '', text)
    # Remove heading markers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove source/DOI lines
    text = re.sub(r'\*?doi:.*', '', text)
    text = re.sub(r'\*?Source:.*', '', text)
    # Remove bracketed notes like [in vitro]
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)
    # Collapse multiple whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


# ============================================================
# TTS Engine: gTTS (primary)
# ============================================================

def generate_tts_gtts(text: str, output_path: str, lang: str = 'en', python_path: str | None = None) -> bool:
    """Generate TTS audio using gTTS (Google). Returns True on success."""
    cleaned = clean_text_for_tts(text)
    runner = python_path or sys.executable
    script = (
        "import sys; "
        "from gtts import gTTS; "
        "gTTS(text=sys.argv[1], lang=sys.argv[2], slow=False).save(sys.argv[3])"
    )
    completed = subprocess.run(
        [runner, '-c', script, cleaned, lang, output_path],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return True
    print(f"WARNING: gTTS generation failed: {completed.stderr.strip() or completed.stdout.strip()}", file=sys.stderr)
    return False


# ============================================================
# TTS Engine: edge-tts (fallback, works in China)
# ============================================================

# Voice mapping for edge-tts
EDGE_TTS_VOICES = {
    'en': 'en-US-AvaNeural',         # Female, US English
    'en-US': 'en-US-AvaNeural',
    'en-GB': 'en-GB-SoniaNeural',    # Female, British English
    'zh-CN': 'zh-CN-XiaoxiaoNeural', # Female, Mandarin Chinese
    'zh': 'zh-CN-XiaoxiaoNeural',
}


def generate_tts_edge(text: str, output_path: str, lang: str = 'en', python_path: str | None = None) -> bool:
    """Generate TTS audio using edge-tts (Microsoft Edge). Returns True on success."""
    cleaned = clean_text_for_tts(text)
    voice = EDGE_TTS_VOICES.get(lang, EDGE_TTS_VOICES['en'])
    runner = python_path or sys.executable
    script = (
        "import asyncio, sys, edge_tts; "
        "async def main():\n"
        "    communicate = edge_tts.Communicate(sys.argv[1], sys.argv[2])\n"
        "    await communicate.save(sys.argv[3])\n"
        "asyncio.run(main())"
    )
    completed = subprocess.run(
        [runner, '-c', script, cleaned, voice, output_path],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return True
    print(f"WARNING: edge-tts generation failed: {completed.stderr.strip() or completed.stdout.strip()}", file=sys.stderr)
    return False


# ============================================================
# Unified TTS interface with auto-fallback
# ============================================================

def generate_tts_audio(text: str, output_path: str, lang: str = 'en',
                       engine: str = 'auto') -> tuple:
    """
    Generate TTS audio with automatic fallback.

    Priority: gTTS -> edge-tts

    Args:
        text: Article text to convert
        output_path: Output MP3 file path
        lang: Language code ('en', 'zh-CN', etc.)
        engine: 'auto' | 'gtts' | 'edge-tts'

    Returns:
        (success: bool, engine_used: str)
    """
    skill_root = Path(__file__).resolve().parents[1]
    env_info = ensure_local_venv(skill_root, skill_root / 'requirements.txt')
    python_path = env_info['python_path']

    if engine == 'edge-tts':
        success = generate_tts_edge(text, output_path, lang, python_path=python_path)
        return (success, 'edge-tts' if success else '')

    if engine == 'gtts':
        success = generate_tts_gtts(text, output_path, lang, python_path=python_path)
        return (success, 'gTTS' if success else '')

    print("Trying gTTS (primary engine)...")
    success = generate_tts_gtts(text, output_path, lang, python_path=python_path)
    if success:
        print(f"OK gTTS succeeded: {output_path}")
        return (True, 'gTTS')

    print("gTTS failed, falling back to edge-tts...")
    success = generate_tts_edge(text, output_path, lang, python_path=python_path)
    if success:
        print(f"OK edge-tts succeeded: {output_path}")
        return (True, 'edge-tts')

    print("ERROR: Both TTS engines failed!", file=sys.stderr)
    return (False, '')


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Nature News Digest TTS Helper')
    parser.add_argument('--top', type=int, default=3, help='Number of top articles to process')
    parser.add_argument('--output-dir', type=str, default=resolve_default_output_dir(),
                        help='Output directory (default: prefer D:/nature-news-digest-sounds, fallback to C:/nature-news-digest-sounds)')
    parser.add_argument('--tts', action='store_true', help='Generate TTS audio files')
    parser.add_argument('--tts-engine', type=str, default='auto',
                        choices=['auto', 'gtts', 'edge-tts'],
                        help='TTS engine: auto (gTTS->edge-tts fallback), gtts, edge-tts')
    parser.add_argument('--tts-lang', type=str, default='en', help='TTS language (en, zh-CN, etc.)')
    args = parser.parse_args()

    print("Nature News Digest TTS Helper")
    print(f"  Top articles: {args.top}")
    print(f"  Output dir: {args.output_dir}")
    print(f"  TTS: {args.tts}")
    print(f"  TTS engine: {args.tts_engine}")
    print(f"  TTS language: {args.tts_lang}")


if __name__ == '__main__':
    main()
