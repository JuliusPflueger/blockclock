"""Write a tiny, atomic freshness proof for local companion tools.

This module intentionally contains no posting or credential handling.  It lets a
separately deployed tool determine whether the screen was rendered from a recent
successful data fetch.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_STATUS_FILE = "/tmp/blockclock-status.json"


def status_file() -> Path:
    return Path(os.environ.get("BLOCKCLOCK_STATUS_FILE", DEFAULT_STATUS_FILE))


def report_success(block_height: int, block_finder_name: str) -> None:
    """Atomically persist the block height that has just been rendered."""
    target = status_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "ok",
        "displayed_block_height": block_height,
        "block_finder_name": block_finder_name,
        "last_successful_update_at": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write(target, payload)


def report_failure() -> None:
    """Preserve the last success time, but make the current state explicitly bad."""
    target = status_file()
    previous = {}
    try:
        previous = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    previous["status"] = "error"
    previous["last_error_at"] = datetime.now(timezone.utc).isoformat()
    _atomic_write(target, previous)


def _atomic_write(target: Path, payload: dict) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False
    ) as temporary:
        json.dump(payload, temporary)
        temporary.write("\n")
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_name = temporary.name
    os.replace(temporary_name, target)
