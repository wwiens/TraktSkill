# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## This is a Claude Skill

`SKILL.md` is the entry point for Claude Code when this repo is installed as a Skill. It contains:
- YAML frontmatter with trigger phrases and metadata
- Command dispatch tables (public vs. personal commands)
- Identifier/slug conventions
- Authentication flow instructions
- Error handling guidance

When answering Trakt.tv queries, Claude reads `SKILL.md` and invokes the `trakt` CLI directly.

## Directory Structure

```
trakt-skill/
├── SKILL.md                   ← Skill entry point (read this first)
├── CLAUDE.md                  ← Developer guidance (this file)
├── pyproject.toml             ← pip install -e . installs the trakt CLI
├── trakt_cli/                 ← Python package
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py
│   ├── cli.py
│   ├── config.py
│   └── output.py
└── references/
    ├── command-reference.md   ← Full CLI usage docs (moved from README.md)
    └── setup-guide.md         ← Setup instructions (moved from GETTING_STARTED.md)
```

## Development Commands

```bash
# Install in editable mode (required before running the CLI)
pip install -e .

# Run the CLI
trakt --help
trakt <command> --help

# Run directly without installing
python -m trakt_cli --help
```

There are no automated tests or linting configuration in this project.

## OAuth Application Credentials (agent86)

Stored in `traktapi.txt` (gitignored). See that file for Client ID, Client Secret, Redirect URI, CORS Origin, and approved features.

## CLI Code Architecture

The `trakt_cli/` package has four modules with clear separation of concerns:

- **`api.py`** — `TraktClient` class: all HTTP calls via `httpx`. Every method maps 1:1 to a Trakt API endpoint. Methods return `(body, pagination_dict)` tuples for paginated endpoints, or plain `dict`/`list` for non-paginated ones. Also contains module-level functions for OAuth flows (`device_code`, `device_token`, `refresh_token`).

- **`config.py`** — Read/write `~/.config/trakt-cli/config.ini`. Handles API key, client secret, and OAuth token persistence. API key resolution order: env var `TRAKT_API_KEY` → config file → `traktapi.txt` in cwd or repo root.

- **`output.py`** — All `rich` console rendering. One function per display format (e.g. `print_show`, `print_movie_list`, `print_sync_history`). Imports nothing from the other CLI modules.

- **`cli.py`** — Click command tree. Each command calls `_make_client()` to get an authenticated `TraktClient`, calls one or more `api.py` methods, and passes results to `output.py` functions. Token auto-refresh happens in `_make_client()`.

### Adding a new command

1. Add method(s) to `TraktClient` in `api.py` (calls `self._get`, `self._post`, etc.)
2. Add a display function to `output.py` (uses `rich` tables/panels)
3. Add a `@click.command()` in `cli.py` attached to the appropriate `@click.group()`
