#!/usr/bin/env python3
"""Local Python environment utilities for nature-news-sound."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REQUIRED_MODULES = ('gtts', 'edge_tts')
SUPPORTED_MINORS = {10, 11, 12, 13, 14}
PREFERRED_MINORS = {10, 11, 12, 13}


def _venv_python_path(runtime_root: Path) -> Path:
    """Return the Python executable path inside scripts/.venv."""
    return runtime_root / '.venv' / ('Scripts/python.exe' if sys.platform.startswith('win') else 'bin/python')


def inspect_local_venv(runtime_root: Path) -> dict:
    """Inspect the local scripts/.venv and report version/module readiness."""
    python_path = _venv_python_path(runtime_root)
    result = {
        'exists': python_path.exists(),
        'python_path': str(python_path),
        'version_ok': False,
        'preferred_version': False,
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
    result['preferred_version'] = info['major'] == 3 and info['minor'] in PREFERRED_MINORS
    result['missing_modules'] = info['missing']
    return result


def ensure_local_venv(runtime_root: Path, requirements_file: Path) -> dict:
    """Reuse or create scripts/.venv and install any missing requirements."""
    venv_dir = runtime_root / '.venv'
    python_path = _venv_python_path(runtime_root)
    status = inspect_local_venv(runtime_root)
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
            raise RuntimeError('Unable to create scripts/.venv with Python 3.10-3.14.')
        status = inspect_local_venv(runtime_root)

    if not status['version_ok']:
        raise RuntimeError('The local scripts/.venv exists, but its Python version is not in 3.10-3.14.')

    if status['missing_modules']:
        subprocess.run(
            [str(python_path), '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True,
        )
        status = inspect_local_venv(runtime_root)
        if status['missing_modules']:
            missing = ', '.join(status['missing_modules'])
            raise RuntimeError(f'Missing required modules after installation: {missing}')

    return {
        'venv_dir': str(venv_dir),
        'python_path': str(python_path),
        'created': created,
        'preferred_version': status['preferred_version'],
    }


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    print(json.dumps(ensure_local_venv(root, root / 'requirements.txt')))
