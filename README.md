# Trakt Skill

An [OpenClaw](https://docs.openclaw.ai/tools/skills) skill and command-line interface for [Trakt.tv](https://trakt.tv) — ask OpenClaw about trending shows, your watchlist, box office results, episode calendars, and more. Also compatible with [Claude Code](https://claude.ai/code) skills.

## What it does

Once installed, you can ask your OpenClaw assistant natural language questions about TV and movies and it will query Trakt.tv on your behalf:

- "What shows are trending right now?"
- "What's on my watchlist?"
- "What movies are in the box office this week?"
- "What episodes air this week?"
- "Check me in to Breaking Bad S03E07"
- "Rate Severance a 9"
- "Add Inception to my watchlist"

Two access tiers:

- **Public** (API key only) — trending, popular, search, calendar, show/movie/episode info, people, lists
- **Personal** (OAuth login) — watch history, watchlist, ratings, collection, check-ins, recommendations

## Installation

**Requirements:** Python 3.9+, a [Trakt.tv](https://trakt.tv) account, and a [Trakt API key](https://trakt.tv/oauth/applications).

```bash
# Clone and install
git clone https://github.com/wwiens/TraktSkill
cd TraktSkill
pip install -e .

# Configure your API key
trakt config set-key YOUR_CLIENT_ID

# Optional: authenticate for personal data
trakt config set-secret YOUR_CLIENT_SECRET
trakt auth login
```

## CLI Usage

```bash
trakt trending                            # trending TV shows
trakt popular                             # popular TV shows
trakt movies boxoffice                    # box office this weekend
trakt movies search inception             # search for a movie
trakt info breaking-bad                   # show details
trakt calendar shows                      # what's airing this week
trakt show episodes breaking-bad 3        # episodes in a season
trakt show people breaking-bad            # cast and crew
trakt people movies bryan-cranston        # person's filmography

# Personal (requires login)
trakt sync history                        # your watch history
trakt sync watchlist                      # your watchlist
trakt sync ratings                        # your ratings
trakt checkin movie the-dark-knight-2008  # check in to a movie
trakt sync rate show severance 9          # rate something
```

Run `trakt --help` or `trakt <command> --help` for full options. See [`references/command-reference.md`](references/command-reference.md) for complete documentation.

## Installing as a Skill

This repo is designed to work as an **[OpenClaw](https://docs.openclaw.ai/tools/skills)** skill. Once installed, Claude will automatically use the `trakt` CLI to answer Trakt.tv questions.

It is also compatible with **Claude Code** skills.

## Tech Stack

- [Click](https://click.palletsprojects.com/) — CLI framework
- [httpx](https://www.python-httpx.org/) — HTTP client
- [Rich](https://github.com/Textualize/rich) — terminal output formatting
- [Trakt.tv API v2](https://trakt.docs.apiary.io/)
