---
name: trakt-skill
description: >
  Use this skill to answer questions about TV shows and movies using the Trakt.tv
  CLI (trakt command). Handles queries like: "what shows are trending?",
  "what's on my watchlist?", "what movies are in the box office this week?",
  "search for a movie called inception", "show me my watch history",
  "what episodes air this week?", "recommend me some shows", "check in to breaking bad",
  "what are the most popular shows of all time?", "add this to my watchlist",
  "rate this show", "look up this IMDB ID". Requires the trakt CLI to be installed
  (pip install -e . in the skill root) and a Trakt API key configured.
compatibility: "Python 3.9+. Install with: pip install -e . Run trakt config set-key KEY to configure."
metadata:
  author: agent86
  version: 1.0.0
  category: entertainment
  tags: [trakt, tv, movies, watchlist, streaming]
---

# Trakt Skill

This skill answers Trakt.tv queries using the `trakt` CLI. Two access tiers:

- **Public** (API key only): trending, popular, search, calendar, people, show/movie/episode info
- **Personal** (OAuth required): sync history, watchlist, ratings, collection, checkin, recommendations

## Prerequisites

Verify the CLI is installed and configured:

```bash
trakt --help
trakt auth status
```

If not installed, run from the skill root:

```bash
pip install -e .
trakt config set-key CLIENT_ID
```

## Command Dispatch

Map user intent to the right `trakt` subcommand. All commands accept `--help` for full options.

### Public — no login needed

| User asks about... | Command |
|---|---|
| Trending TV shows | `trakt trending` |
| Popular TV shows | `trakt popular` |
| Most anticipated shows | `trakt anticipated` |
| Search for a show | `trakt search QUERY` |
| Show details | `trakt info SHOW_ID` |
| Shows airing this week | `trakt calendar shows` |
| Season premieres/finales | `trakt calendar premieres` / `trakt calendar finales` |
| New series premiering | `trakt calendar new` |
| Trending movies | `trakt movies trending` |
| Popular movies | `trakt movies popular` |
| Box office this weekend | `trakt movies boxoffice` |
| Search for a movie | `trakt movies search QUERY` |
| Movie details | `trakt movies info MOVIE_ID` |
| Movies releasing soon | `trakt calendar movies` |
| Show seasons | `trakt show seasons SHOW_ID` |
| Episodes in a season | `trakt show episodes SHOW_ID SEASON` |
| Show cast/crew | `trakt show people SHOW_ID` |
| Related shows | `trakt show related SHOW_ID` |
| Next/last episode | `trakt show next SHOW_ID` / `trakt show last SHOW_ID` |
| Person info / credits | `trakt people info PERSON_ID` |
| Person's movie credits | `trakt people movies PERSON_ID` |
| Person's show credits | `trakt people shows PERSON_ID` |
| Look up by IMDB/TMDB/TVDB | `trakt lookup imdb TT_ID` |
| Public Trakt lists | `trakt lists trending` / `trakt lists popular` |

### Personal — requires `trakt auth login`

| User asks about... | Command |
|---|---|
| Watch history | `trakt sync history` |
| Watchlist | `trakt sync watchlist` |
| Ratings | `trakt sync ratings` |
| Collection | `trakt sync collection movies` / `shows` |
| Everything watched | `trakt sync watched movies` / `shows` |
| Paused playback | `trakt sync playback` |
| Recommendations | `trakt recommendations movies` / `shows` |
| Check in to movie | `trakt checkin movie SLUG` |
| Check in to episode | `trakt checkin episode SHOW SEASON EP` |
| Remove check-in | `trakt checkin delete` |
| Add to watchlist | `trakt sync watchlist-add movie SLUG` |
| Remove from watchlist | `trakt sync watchlist-remove movie SLUG` |
| Rate something (1-10) | `trakt sync rate movie SLUG RATING` |
| Remove a rating | `trakt sync unrate movie SLUG` |
| Mark as watched | `trakt sync add-history movie SLUG` |
| My profile | `trakt users profile` |
| My stats | `trakt users stats` |

## Identifiers

Most commands use **slugs** (URL-safe titles): `breaking-bad`, `the-dark-knight-2008`, `bryan-cranston`.

When a user gives a name, convert to slug (lowercase, spaces→hyphens, drop special chars) or use `trakt search` / `trakt movies search` first to find the correct slug.

You can also use IMDB IDs (`tt0903747`) or Trakt integer IDs via `trakt lookup imdb TT_ID`.

## Pagination and Periods

- All list commands accept `--page/-p` and `--limit/-n` (default: 10)
- "Period" commands (`favorited`, `played`, `watched`, `collected`) accept `--period`: `daily`, `weekly` (default), `monthly`, `all`
- When output shows `Page 1/N  X total results`, relay that to the user and offer to fetch more

## Authentication Flow

If a command needs auth:

1. Set API key: `trakt config set-key CLIENT_ID`
2. Set client secret: `trakt config set-secret CLIENT_SECRET`
3. Start login: `trakt auth login` — CLI prints a code and `https://trakt.tv/activate`
4. User visits URL, enters code, approves
5. CLI confirms; tokens auto-refresh 1 hour before expiry

## Error Handling

| Error | Fix |
|---|---|
| `No API key found` | `trakt config set-key KEY` |
| HTTP 401 | `trakt auth login` |
| HTTP 409 on checkin | Already checked in — `trakt checkin delete` first |
| HTTP 404 | Bad slug — use `trakt search` to verify |
| `No results found` | Broaden search or check spelling |

## Examples

```bash
trakt trending                          # what's trending on TV
trakt movies search inception           # find movies
trakt info breaking-bad                 # show details
trakt calendar shows                    # what's airing this week
trakt sync watchlist                    # my watchlist
trakt sync watchlist-add show severance # add to watchlist
trakt checkin movie the-dark-knight-2008
trakt movies boxoffice
trakt show people breaking-bad
trakt people movies bryan-cranston
```

For full option details, consult `references/command-reference.md` or run `trakt <command> --help`.
