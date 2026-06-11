#!/usr/bin/env python3
"""Local Python environment utilities for nature-news-digest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REQUIRED_MODULES = ('gtts', 'edge_tts')
SUPPORTED_MINORS = {10, 11, 12, 13, 14}


def inspect_local_venv(skill_root: Path) -> dict:
    """Inspect the skill-local .venv and report version/module readiness."""
    venv_dir = skill_root / '.venv'
    python_path = venv_dir / ('Scripts/python.exe' if sys.platform.startswith('win') else 'bin/python')
    result = {
        'exists': python_path.exists(),
        'python_path': str(python_path),
        'version_ok': False,
        'missing_modules': list(REQUIRED_MODULES),
    }
    if not python_path.exists():
        return result

    script = (
        "import importlib.util, json, sys; "
        "mods = ['gtts', 'edge_tts']; "
        "missing = [m for m in mods if importlib.util.find_spec(m) is None]; "
        "print(json.dumps({"
        "'major': sys.version_info.major, "
        "'minor': sys.version_info.minor, "
        "'missing': missing"
        "}))"
    )
    probe = subprocess.run(
        [str(python_path), '-c', script],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return result

    info = json.loads(probe.stdout.strip())
    result['version_ok'] = info['major'] == 3 and info['minor'] in SUPPORTED_MINORS
    result['missing_modules'] = info['missing']
    return result


def ensure_local_venv(skill_root: Path, requirements_file: Path) -> dict:
    """Reuse or create the skill-local .venv and install any missing requirements."""
    venv_dir = skill_root / '.venv'
    python_path = venv_dir / ('Scripts/python.exe' if sys.platform.startswith('win') else 'bin/python')
    status = inspect_local_venv(skill_root)
    created = False

    if not status['exists']:
        for candidate in ('python3.14', 'python3.13', 'python3.12', 'python3.11', 'python3.10', 'python3', 'python'):
            try:
                subprocess.run([candidate, '-m', 'venv', str(venv_dir)], check=True, capture_output=True, text=True)
                created = True
                break
            except (OSError, subprocess.CalledProcessError):
                continue
        if not created:
            raise RuntimeError('Unable to create .venv with Python 3.10-3.14 under the skill root.')
        status = inspect_local_venv(skill_root)

    if not status['version_ok']:
        raise RuntimeError('The skill-local .venv exists, but its Python version is not in 3.10-3.14.')

    if status['missing_modules']:
        subprocess.run(
            [str(python_path), '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True,
        )
        status = inspect_local_venv(skill_root)
        if status['missing_modules']:
            missing = ', '.join(status['missing_modules'])
            raise RuntimeError(f'Missing required modules after installation: {missing}')

    return {
        'venv_dir': str(venv_dir),
        'python_path': str(python_path),
        'created': created,
    }


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(ensure_local_venv(root, root / 'requirements.txt')))
