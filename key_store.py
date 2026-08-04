"""Simple local lifetime-key store for the safe Discord bot."""

from __future__ import annotations

import json
import secrets
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_KEY_STORE_PATH = Path("data/lifetime_keys.json")


@dataclass(frozen=True)
class LifetimeKey:
    key: str
    user_id: int
    created_by: int
    created_at: str
    note: str = ""


def generate_lifetime_key() -> str:
    """Generate a Discord-friendly lifetime access key."""
    return f"LIFE-{secrets.token_urlsafe(24)}"


def load_lifetime_keys(path: Path = DEFAULT_KEY_STORE_PATH) -> dict[str, LifetimeKey]:
    """Load all lifetime keys from disk."""
    if not path.exists():
        return {}

    raw = json.loads(path.read_text(encoding="utf-8"))
    return {key: LifetimeKey(**value) for key, value in raw.items()}


def save_lifetime_keys(
    keys: dict[str, LifetimeKey],
    path: Path = DEFAULT_KEY_STORE_PATH,
) -> None:
    """Persist all lifetime keys to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: asdict(value) for key, value in keys.items()}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def create_lifetime_key(
    user_id: int,
    created_by: int,
    note: str = "",
    path: Path = DEFAULT_KEY_STORE_PATH,
) -> LifetimeKey:
    """Create and store a lifetime key for one Discord user."""
    keys = load_lifetime_keys(path)
    key = generate_lifetime_key()
    lifetime_key = LifetimeKey(
        key=key,
        user_id=user_id,
        created_by=created_by,
        created_at=datetime.now(UTC).isoformat(),
        note=note.strip()[:120],
    )
    keys[key] = lifetime_key
    save_lifetime_keys(keys, path)
    return lifetime_key


def user_has_lifetime_key(user_id: int, path: Path = DEFAULT_KEY_STORE_PATH) -> bool:
    """Return whether a Discord user has at least one lifetime key."""
    return any(item.user_id == user_id for item in load_lifetime_keys(path).values())
