from __future__ import annotations

import os
import re
import configparser
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "trakt-cli"
_CONFIG_FILE = _CONFIG_DIR / "config.ini"
_CLIENT_ID_RE = re.compile(r"Client ID:\s*([0-9a-f]{64})", re.IGNORECASE)
_CLIENT_SECRET_RE = re.compile(r"Client Secret:\s*([0-9a-f]{64})", re.IGNORECASE)


def load_api_key() -> str | None:
    # 1. Environment variable
    key = os.environ.get("TRAKT_API_KEY")
    if key:
        return key.strip()

    # 2. ~/.config/trakt-cli/config.ini
    if _CONFIG_FILE.exists():
        cfg = configparser.ConfigParser()
        cfg.read(_CONFIG_FILE)
        key = cfg.get("trakt", "api_key", fallback=None)
        if key:
            return key.strip()

    # 3. ./traktapi.txt relative to cwd, then repo root alongside this file
    candidates = [
        Path.cwd() / "traktapi.txt",
        Path(__file__).parent.parent / "traktapi.txt",
    ]
    for path in candidates:
        if path.exists():
            match = _CLIENT_ID_RE.search(path.read_text())
            if match:
                return match.group(1)

    return None


def load_client_secret() -> str | None:
    secret = os.environ.get("TRAKT_CLIENT_SECRET")
    if secret:
        return secret.strip()

    if _CONFIG_FILE.exists():
        cfg = configparser.ConfigParser()
        cfg.read(_CONFIG_FILE)
        secret = cfg.get("trakt", "client_secret", fallback=None)
        if secret:
            return secret.strip()

    candidates = [
        Path.cwd() / "traktapi.txt",
        Path(__file__).parent.parent / "traktapi.txt",
    ]
    for path in candidates:
        if path.exists():
            match = _CLIENT_SECRET_RE.search(path.read_text())
            if match:
                return match.group(1)

    return None


def save_client_secret(secret: str) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = configparser.ConfigParser()
    if _CONFIG_FILE.exists():
        cfg.read(_CONFIG_FILE)
    if not cfg.has_section("trakt"):
        cfg.add_section("trakt")
    cfg.set("trakt", "client_secret", secret)
    with _CONFIG_FILE.open("w") as f:
        cfg.write(f)


def load_token() -> dict | None:
    if not _CONFIG_FILE.exists():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(_CONFIG_FILE)
    access_token = cfg.get("trakt", "access_token", fallback=None)
    if not access_token:
        return None
    return {
        "access_token": access_token,
        "refresh_token": cfg.get("trakt", "refresh_token", fallback=None),
        "expires_in": cfg.getint("trakt", "expires_in", fallback=0),
        "created_at": cfg.getint("trakt", "created_at", fallback=0),
    }


def save_token(token_data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = configparser.ConfigParser()
    if _CONFIG_FILE.exists():
        cfg.read(_CONFIG_FILE)
    if not cfg.has_section("trakt"):
        cfg.add_section("trakt")
    cfg.set("trakt", "access_token", token_data.get("access_token", ""))
    cfg.set("trakt", "refresh_token", token_data.get("refresh_token", "") or "")
    cfg.set("trakt", "expires_in", str(token_data.get("expires_in", 0)))
    cfg.set("trakt", "created_at", str(token_data.get("created_at", 0)))
    with _CONFIG_FILE.open("w") as f:
        cfg.write(f)


def clear_token() -> None:
    if not _CONFIG_FILE.exists():
        return
    cfg = configparser.ConfigParser()
    cfg.read(_CONFIG_FILE)
    if cfg.has_section("trakt"):
        for field in ("access_token", "refresh_token", "expires_in", "created_at"):
            cfg.remove_option("trakt", field)
    with _CONFIG_FILE.open("w") as f:
        cfg.write(f)


def save_api_key(key: str) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = configparser.ConfigParser()
    if _CONFIG_FILE.exists():
        cfg.read(_CONFIG_FILE)
    if not cfg.has_section("trakt"):
        cfg.add_section("trakt")
    cfg.set("trakt", "api_key", key)
    with _CONFIG_FILE.open("w") as f:
        cfg.write(f)
