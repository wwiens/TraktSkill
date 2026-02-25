# trakt-cli

A Python command-line tool for querying show, movie, and personal watch data from [Trakt.tv](https://trakt.tv). Public browsing requires only an API key. Authenticated commands (sync, checkin, recommendations, etc.) require a full OAuth login.

## Requirements

- Python 3.9+
- A Trakt API key (Client ID from a registered Trakt application)

## Installation

From the repository root:

```bash
pip install -e .
```

This installs the `trakt` command. If pip warns that the script directory is not on PATH, add it:

```bash
export PATH="/Users/$(whoami)/Library/Python/3.9/bin:$PATH"
```

## Configuration

The CLI looks for your API key in three places, in priority order:

1. **Environment variable** — `TRAKT_API_KEY`
2. **Config file** — `~/.config/trakt-cli/config.ini`
3. **`traktapi.txt`** — a file in the current working directory containing a `Client ID: <hex>` line

To persist your key to the config file:

```bash
trakt config set-key YOUR_CLIENT_ID
```

To persist your client secret (required for OAuth login):

```bash
trakt config set-secret YOUR_CLIENT_SECRET
```

If you're running from the repository root, the included `traktapi.txt` is picked up automatically and no further setup is needed.

---

## Authentication — `trakt auth`

Authenticated commands require a Trakt OAuth token. The CLI uses the Device OAuth flow — no browser redirect needed.

### `trakt auth login`

Start the Device OAuth flow. Prints a code and URL, then polls until you authorize in a browser.

```bash
trakt auth login
```

### `trakt auth status`

Show whether a token is stored and whether it is still valid.

```bash
trakt auth status
```

### `trakt auth refresh`

Manually force a token refresh using the stored refresh token.

```bash
trakt auth refresh
```

### `trakt auth logout`

Clear the stored access and refresh tokens.

```bash
trakt auth logout
```

---

## Shows

Top-level show commands — invoked directly as `trakt <command>`.

### `trakt search QUERY`

Search for shows by title. The query can be multiple words — no quotes needed.

```bash
trakt search breaking bad
trakt search "game of thrones"
trakt search the wire --limit 5
trakt search sopranos --page 2 --limit 20
```

Output columns: `#`, `Title`, `Year`, `Score`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt info SHOW_ID`

Show full details for a specific show. The ID can be a Trakt slug, an IMDB ID, or a Trakt integer ID.

```bash
trakt info breaking-bad
trakt info tt0903747
trakt info 1388
```

Displays a panel with: status, network, country, language, runtime, rating, aired episodes, genres, external IDs (Trakt slug, IMDB, TMDB, TVDB), and overview.

---

### `trakt trending`

Shows being watched by the most Trakt users right now.

```bash
trakt trending
trakt trending --limit 25
trakt trending --page 2
```

Output columns: `#`, `Watchers`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt popular`

Most popular shows of all time on Trakt, ranked by user activity.

```bash
trakt popular
trakt popular --limit 20
trakt popular --page 3 --limit 50
```

Output columns: `#`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt favorited`

Most favorited shows for a time period.

```bash
trakt favorited
trakt favorited --period all --limit 20
```

Output columns: `#`, `Users`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt played`

Most played shows by total play count for a time period. A single user rewatching episodes counts toward the total.

```bash
trakt played
trakt played --period monthly --limit 10
```

Output columns: `#`, `Plays`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt watched`

Most watched shows by unique user count for a time period. Unlike `played`, each user is only counted once.

```bash
trakt watched
trakt watched --period daily
```

Output columns: `#`, `Watchers`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt collected`

Most collected shows by unique collector count for a time period.

```bash
trakt collected
trakt collected --period all --limit 25
```

Output columns: `#`, `Collectors`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt anticipated`

Most anticipated upcoming shows, ranked by how many Trakt lists they appear on.

```bash
trakt anticipated
trakt anticipated --limit 20
```

Output columns: `#`, `Lists`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt updates`

Shows updated since a given date. Useful for syncing or tracking recent metadata changes. The start date can be at most 30 days in the past, and is only accurate to the hour.

```bash
trakt updates
trakt updates --since 2026-02-20T12:00:00Z
trakt updates --since 2026-02-01 --limit 50
```

Defaults to 24 hours ago when `--since` is not provided.

Output columns: `#`, `Updated At`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--since` | `-s` | 24 hours ago | Start date (`YYYY-MM-DD` or `YYYY-MM-DDTHH:00:00Z`) |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

## `trakt show` — Show Sub-resources

Drill-down commands for a specific show. Each takes a show ID (slug, IMDB ID, or Trakt integer ID) as its first argument.

```bash
trakt show --help
```

### `trakt show seasons SHOW_ID`

List all seasons with episode counts and ratings.

```bash
trakt show seasons breaking-bad
```

Output columns: `Season`, `Title`, `Episodes`, `Aired`, `Rating`

---

### `trakt show episodes SHOW_ID SEASON`

List all episodes in a season.

```bash
trakt show episodes breaking-bad 1
trakt show episodes game-of-thrones 3
```

Output columns: `Ep`, `Title`, `Trakt ID`

---

### `trakt show people SHOW_ID`

Cast (top 20) and crew (directing, writing, created by, production) with episode counts.

```bash
trakt show people breaking-bad
```

Cast columns: `Name`, `Characters`, `Eps`, `Slug`
Crew columns: `Name`, `Job`, `Eps`, `Slug`

---

### `trakt show related SHOW_ID`

Shows related to a given show.

```bash
trakt show related breaking-bad
trakt show related breaking-bad --limit 20
```

Output columns: `#`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt show ratings SHOW_ID`

Rating score and full 1–10 distribution bar chart.

```bash
trakt show ratings breaking-bad
```

---

### `trakt show stats SHOW_ID`

Watchers, plays, collectors, collected episodes, comments, lists, votes, and favorited count.

```bash
trakt show stats breaking-bad
```

---

### `trakt show aliases SHOW_ID`

Alternate titles by country.

```bash
trakt show aliases game-of-thrones
```

Output columns: `Country`, `Title`

---

### `trakt show watching SHOW_ID`

Users currently watching the show. Prints "Nobody is watching right now." when the count is zero.

```bash
trakt show watching the-pitt-2025
```

Output columns: `Username`, `Name`, `VIP`

---

### `trakt show next SHOW_ID`

Next episode scheduled to air. Prints "No next episode found." for ended shows.

```bash
trakt show next the-last-of-us
```

---

### `trakt show last SHOW_ID`

Most recently aired episode.

```bash
trakt show last breaking-bad
```

---

### `trakt show comments SHOW_ID`

Comments on a show, sorted by newest by default.

```bash
trakt show comments breaking-bad
trakt show comments breaking-bad --sort likes --limit 20
```

Output: one panel per comment showing text, author, date, likes, and reply count.

| Option | Default | Description |
|--------|---------|-------------|
| `--sort` | `newest` | `newest`, `oldest`, `likes`, `replies`, `highest`, `lowest`, `plays`, `watched` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt show progress SHOW_ID`

Your watched progress for a show — how many episodes you've seen per season, overall completion percentage, and next episode to watch. Requires auth.

```bash
trakt show progress breaking-bad
trakt show progress breaking-bad --specials
```

| Option | Description |
|--------|-------------|
| `--specials` | Include season 0 specials |
| `--hidden` | Include hidden seasons |

---

### `trakt show collected-progress SHOW_ID`

Your collection progress for a show — how many episodes you've collected per season. Requires auth.

```bash
trakt show collected-progress breaking-bad
```

| Option | Description |
|--------|-------------|
| `--specials` | Include season 0 specials |
| `--hidden` | Include hidden seasons |

---

### `trakt show season-info SHOW_ID SEASON`

Detailed info for a specific season — first aired date, episode count, network, rating, and overview.

```bash
trakt show season-info breaking-bad 1
```

---

### `trakt show season-people SHOW_ID SEASON`

Cast and crew for a specific season.

```bash
trakt show season-people breaking-bad 1
```

Cast columns: `Name`, `Characters`, `Eps`, `Slug`
Crew columns: `Name`, `Job`, `Eps`, `Slug`

---

### `trakt show season-ratings SHOW_ID SEASON`

Rating score and 1–10 distribution bar chart for a specific season.

```bash
trakt show season-ratings breaking-bad 1
```

---

### `trakt show season-stats SHOW_ID SEASON`

Play, collect, and engagement stats for a specific season.

```bash
trakt show season-stats breaking-bad 1
```

---

### `trakt show season-watching SHOW_ID SEASON`

Users currently watching a specific season.

```bash
trakt show season-watching the-pitt-2025 1
```

Output columns: `Username`, `Name`, `VIP`

---

### `trakt show season-comments SHOW_ID SEASON`

Comments on a specific season.

```bash
trakt show season-comments breaking-bad 1
trakt show season-comments breaking-bad 1 --sort likes
```

| Option | Default | Description |
|--------|---------|-------------|
| `--sort` | `newest` | `newest`, `oldest`, `likes`, `replies`, `highest`, `lowest`, `plays`, `watched` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt show episode SHOW_ID SEASON NUMBER`

Detailed info for a specific episode — type, first aired date, runtime, rating, and overview.

```bash
trakt show episode breaking-bad 1 1
trakt show episode game-of-thrones 3 9
```

---

### `trakt show episode-people SHOW_ID SEASON NUMBER`

Cast and crew for a specific episode.

```bash
trakt show episode-people breaking-bad 1 1
```

Cast columns: `Name`, `Characters`, `Eps`, `Slug`
Crew columns: `Name`, `Job`, `Eps`, `Slug`

---

### `trakt show episode-ratings SHOW_ID SEASON NUMBER`

Rating score and 1–10 distribution bar chart for a specific episode.

```bash
trakt show episode-ratings breaking-bad 1 1
```

---

### `trakt show episode-stats SHOW_ID SEASON NUMBER`

Play, collect, and engagement stats for a specific episode.

```bash
trakt show episode-stats breaking-bad 1 1
```

---

### `trakt show episode-watching SHOW_ID SEASON NUMBER`

Users currently watching a specific episode.

```bash
trakt show episode-watching the-pitt-2025 1 3
```

Output columns: `Username`, `Name`, `VIP`

---

### `trakt show episode-comments SHOW_ID SEASON NUMBER`

Comments on a specific episode.

```bash
trakt show episode-comments breaking-bad 1 1
trakt show episode-comments breaking-bad 1 1 --sort likes
```

| Option | Default | Description |
|--------|---------|-------------|
| `--sort` | `newest` | `newest`, `oldest`, `likes`, `replies`, `highest`, `lowest`, `plays`, `watched` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

## `trakt movies` — Movie Commands

All movie commands live under the `trakt movies` subgroup.

```bash
trakt movies --help
```

### `trakt movies search QUERY`

Search for movies by title.

```bash
trakt movies search the dark knight
trakt movies search "fight club" --limit 5
trakt movies search inception --page 2
```

Output columns: `#`, `Title`, `Year`, `Score`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies info MOVIE_ID`

Show full details for a movie. The ID can be a Trakt slug, an IMDB ID, or a Trakt integer ID.

```bash
trakt movies info the-dark-knight-2008
trakt movies info tt0468569
trakt movies info 16
```

Displays a panel with: status, release date, runtime, certification, country, languages, rating, genres, tagline, homepage, trailer, external IDs (Trakt slug, IMDB, TMDB), and overview.

---

### `trakt movies trending`

Most watched movies over the last 24 hours.

```bash
trakt movies trending
trakt movies trending --limit 25
```

Output columns: `#`, `Watchers`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies popular`

Most popular movies of all time, ranked by rating and number of ratings.

```bash
trakt movies popular
trakt movies popular --limit 20 --page 2
```

Output columns: `#`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies favorited`

Most favorited movies for a time period.

```bash
trakt movies favorited
trakt movies favorited --period all
```

Output columns: `#`, `Users`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies played`

Most played movies by total play count for a time period.

```bash
trakt movies played
trakt movies played --period monthly --limit 10
```

Output columns: `#`, `Plays`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies watched`

Most watched movies by unique user count for a time period.

```bash
trakt movies watched
trakt movies watched --period daily
```

Output columns: `#`, `Watchers`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies collected`

Most collected movies by unique collector count for a time period.

```bash
trakt movies collected
trakt movies collected --period all --limit 25
```

Output columns: `#`, `Collectors`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-t` | `weekly` | `daily`, `weekly`, `monthly`, or `all` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies anticipated`

Most anticipated upcoming movies, ranked by how many Trakt lists they appear on.

```bash
trakt movies anticipated
trakt movies anticipated --limit 20
```

Output columns: `#`, `Lists`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies boxoffice`

Top 10 U.S. box office movies from last weekend. Updated every Monday morning. No pagination — always returns exactly 10 results.

```bash
trakt movies boxoffice
```

Output columns: `#`, `Revenue (USD)`, `Title`, `Year`, `Slug`

---

### `trakt movies updates`

Movies updated since a given date (max 30 days ago). Defaults to 24 hours ago.

```bash
trakt movies updates
trakt movies updates --since 2026-02-20T12:00:00Z
```

Output columns: `#`, `Updated At`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--since` | `-s` | 24 hours ago | Start date (`YYYY-MM-DD` or `YYYY-MM-DDTHH:00:00Z`) |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies people MOVIE_ID`

Cast (top 20) and key crew (directing, writing, created by, production).

```bash
trakt movies people the-dark-knight-2008
```

Cast columns: `Name`, `Characters`, `Slug`
Crew columns: `Name`, `Job`, `Slug`

---

### `trakt movies related MOVIE_ID`

Movies related to a given movie.

```bash
trakt movies related the-dark-knight-2008
trakt movies related the-dark-knight-2008 --limit 10
```

Output columns: `#`, `Title`, `Year`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt movies ratings MOVIE_ID`

Rating score and full 1–10 distribution bar chart.

```bash
trakt movies ratings the-dark-knight-2008
```

---

### `trakt movies stats MOVIE_ID`

Watchers, plays, collectors, comments, lists, votes, and favorited count.

```bash
trakt movies stats the-dark-knight-2008
```

---

### `trakt movies aliases MOVIE_ID`

Alternate titles by country.

```bash
trakt movies aliases the-dark-knight-2008
```

Output columns: `Country`, `Title`

---

### `trakt movies watching MOVIE_ID`

Users currently watching the movie. Prints "Nobody is watching right now." when the count is zero.

```bash
trakt movies watching inception-2010
```

Output columns: `Username`, `Name`, `VIP`

---

## `trakt calendar` — Calendar

All calendar commands live under the `trakt calendar` subgroup. Results are grouped by date with a bold header for each day. When authenticated, the `my` calendar endpoint is used; otherwise, the `all` endpoint is used.

```bash
trakt calendar --help
```

All calendar commands share the same two options:

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--date` | `-d` | today | Start date (`YYYY-MM-DD`) |
| `--days` | `-D` | `7` | Number of days to include |

---

### `trakt calendar shows`

All episodes airing across any show in the given date range.

```bash
trakt calendar shows
trakt calendar shows --days 3
trakt calendar shows --date 2026-03-01 --days 14
```

Output: date headers, then per episode — `Show`, `S##E##`, `"Episode Title"`, `HH:MM UTC`

---

### `trakt calendar new`

New series premiering (series premiere episodes only).

```bash
trakt calendar new
trakt calendar new --days 14
```

Same output format as `calendar shows`.

---

### `trakt calendar premieres`

Season premieres airing (includes series, season, and mid-season premieres).

```bash
trakt calendar premieres
trakt calendar premieres --date 2026-03-01
```

Same output format as `calendar shows`.

---

### `trakt calendar finales`

Season finales airing in the date range.

```bash
trakt calendar finales
trakt calendar finales --days 14
```

Same output format as `calendar shows`.

---

### `trakt calendar movies`

All movies with a release date in the given range.

```bash
trakt calendar movies
trakt calendar movies --days 3
```

Output: date headers, then per movie — `Title`, `Year`, `Slug`

---

### `trakt calendar streaming`

Movies hitting U.S. streaming platforms in the given date range.

```bash
trakt calendar streaming
trakt calendar streaming --days 14
```

Same output format as `calendar movies`.

---

### `trakt calendar dvd`

Movies releasing on U.S. DVD in the given date range.

```bash
trakt calendar dvd
trakt calendar dvd --date 2026-03-01 --days 7
```

Same output format as `calendar movies`.

---

## `trakt lookup`

Look up any item by its external ID. Resolves IMDB, TMDB, TVDB, or Trakt integer IDs to their Trakt entry.

```bash
trakt lookup imdb tt0903747
trakt lookup tmdb 155 --type movie
trakt lookup tvdb 81189 --type show
trakt lookup trakt 1388 --type show
trakt lookup imdb nm0227759 --type person
```

Valid `ID_TYPE` values: `imdb`, `tmdb`, `tvdb`, `trakt`

Output columns: `Type`, `Title / Name`, `Year`, `Detail`, `Slug / ID`

> **Note:** IMDB `nm` person IDs require `--type person`. TMDB and TVDB IDs are not globally unique across types, so `--type` is recommended for those.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--type` | `-t` | _(all types)_ | Restrict to: `movie`, `show`, `episode`, `person`, `list` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

## `trakt people` — People

Look up a person and their credits.

```bash
trakt people --help
```

### `trakt people info PERSON_ID`

Detailed info for a person. The ID can be a Trakt slug, an IMDB `nm` ID, or a Trakt integer ID.

```bash
trakt people info bryan-cranston
trakt people info nm0186505
```

Displays a panel with: birthday, birthplace, death, gender, known for, homepage, social links, external IDs, and biography.

---

### `trakt people movies PERSON_ID`

All movie credits for a person, broken out by role.

```bash
trakt people movies bryan-cranston
```

Tables for each role type (Cast, Directing, Writing, etc.)
Columns: `Characters / Job`, `Title`, `Year`, `Slug`

---

### `trakt people shows PERSON_ID`

All show credits for a person, broken out by role.

```bash
trakt people shows bryan-cranston
```

Tables for each role type (Cast, Directing, Writing, etc.)
Columns: `Characters / Job`, `Eps`, `Title`, `Year`, `Slug`

---

## `trakt lists` — Public Lists

Browse public Trakt lists.

```bash
trakt lists --help
```

### `trakt lists trending`

Lists with the most likes and comments over the last 7 days.

```bash
trakt lists trending
trakt lists trending --type official --limit 20
```

Output columns: `Name`, `By`, `Items`, `Likes`, `Comments`, `Slug`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | `personal` | `personal` or `official` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt lists popular`

Most popular lists of all time.

```bash
trakt lists popular
trakt lists popular --type official
```

Output columns: `Name`, `By`, `Items`, `Likes`, `Comments`, `Slug`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | `personal` | `personal` or `official` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt lists get LIST_ID`

Fetch metadata for a single public list by its Trakt integer ID.

```bash
trakt lists get 12345
```

Displays a panel with: description, owner, privacy, item count, likes, comments, sort, link, and Trakt/slug IDs.

---

### `trakt lists items LIST_ID`

Items on a public list.

```bash
trakt lists items 12345
trakt lists items 12345 --type movie
trakt lists items 12345 --limit 50
```

Output columns: `#`, `Type`, `Title`, `Ep`, `Notes`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | _(all)_ | `movie`, `show`, `season`, `episode`, or `person` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt lists like LIST_ID`

Like a public list. Requires auth.

```bash
trakt lists like 12345
```

---

### `trakt lists unlike LIST_ID`

Remove your like from a list. Requires auth.

```bash
trakt lists unlike 12345
```

---

## `trakt comments` — Comments

Read and write comments on movies, shows, episodes, and seasons.

```bash
trakt comments --help
```

### `trakt comments get COMMENT_ID`

Fetch a single comment by its Trakt integer ID.

```bash
trakt comments get 98765
```

Displays a panel with the comment text, author, date, likes, reply count, and spoiler/review flags.

---

### `trakt comments post TYPE ID_OR_SLUG TEXT`

Post a new comment. Requires auth.

```bash
trakt comments post show breaking-bad "One of the greatest shows ever made."
trakt comments post movie the-dark-knight-2008 "Ledger's Joker is unmatched." --spoiler
trakt comments post episode 12345 "What an ending."
```

`TYPE` is `movie`, `show`, `season`, or `episode`.
`ID_OR_SLUG` is a Trakt slug (e.g. `breaking-bad`) or numeric Trakt ID.

| Option | Description |
|--------|-------------|
| `--spoiler` | Mark the comment as containing spoilers |

---

### `trakt comments update COMMENT_ID TEXT`

Update the text of your own comment. Requires auth.

```bash
trakt comments update 98765 "Updated text here."
trakt comments update 98765 "Updated spoiler text." --spoiler
```

| Option | Description |
|--------|-------------|
| `--spoiler` | Mark as spoiler |

---

### `trakt comments delete COMMENT_ID`

Delete your own comment. Requires auth.

```bash
trakt comments delete 98765
```

---

### `trakt comments replies COMMENT_ID`

List replies to a comment.

```bash
trakt comments replies 98765
trakt comments replies 98765 --limit 20
```

Output: one panel per reply with text, author, date, likes, and reply count.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `10` | Results per page |

---

### `trakt comments reply COMMENT_ID TEXT`

Post a reply to an existing comment. Requires auth.

```bash
trakt comments reply 98765 "I completely agree."
trakt comments reply 98765 "Spoiler reply here." --spoiler
```

| Option | Description |
|--------|-------------|
| `--spoiler` | Mark as spoiler |

---

### `trakt comments like COMMENT_ID`

Like a comment. Requires auth.

```bash
trakt comments like 98765
```

---

### `trakt comments unlike COMMENT_ID`

Remove your like from a comment. Requires auth.

```bash
trakt comments unlike 98765
```

---

## `trakt checkin` — Check-in

Manually record what you're watching right now. Only one active checkin is allowed at a time — checking in to something new replaces the previous one. Requires auth.

```bash
trakt checkin --help
```

### `trakt checkin movie SLUG`

Check in to a movie by its Trakt slug.

```bash
trakt checkin movie the-dark-knight-2008
trakt checkin movie the-dark-knight-2008 --message "Movie night!"
```

Displays a confirmation with the movie title and start time.

| Option | Description |
|--------|-------------|
| `--message` | Optional message for social sharing |

---

### `trakt checkin episode SHOW_SLUG SEASON NUMBER`

Check in to a specific episode.

```bash
trakt checkin episode breaking-bad 1 1
trakt checkin episode the-last-of-us 2 3 --message "Finally watching this"
```

Displays a confirmation with the episode title and start time.

| Option | Description |
|--------|-------------|
| `--message` | Optional message for social sharing |

---

### `trakt checkin delete`

Remove any active checkin.

```bash
trakt checkin delete
```

---

## `trakt recommendations` — Recommendations

Personalized movie and show recommendations based on your watch history. Requires auth.

```bash
trakt recommendations --help
```

### `trakt recommendations movies`

Personalized movie recommendations.

```bash
trakt recommendations movies
trakt recommendations movies --limit 25
trakt recommendations movies --ignore-collected --ignore-watchlisted
```

Output columns: `#`, `Title`, `Year`, `Slug`, `Favorited by`

| Option | Default | Description |
|--------|---------|-------------|
| `--limit` / `-n` | `10` | Number of results (max 100) |
| `--ignore-collected` | off | Exclude movies already in your collection |
| `--ignore-watchlisted` | off | Exclude movies already on your watchlist |

---

### `trakt recommendations shows`

Personalized show recommendations.

```bash
trakt recommendations shows
trakt recommendations shows --limit 25 --ignore-collected
```

Output columns: `#`, `Title`, `Year`, `Slug`, `Favorited by`

| Option | Default | Description |
|--------|---------|-------------|
| `--limit` / `-n` | `10` | Number of results (max 100) |
| `--ignore-collected` | off | Exclude shows already in your collection |
| `--ignore-watchlisted` | off | Exclude shows already on your watchlist |

---

### `trakt recommendations hide TYPE SLUG`

Hide a movie or show so it no longer appears in recommendations. Requires auth.

```bash
trakt recommendations hide movie the-dark-knight-2008
trakt recommendations hide show lost
```

`TYPE` is `movie` or `show`.

---

## `trakt sync` — Your Watch Data

Commands for reading and writing your personal Trakt data. All commands require auth.

```bash
trakt sync --help
```

### `trakt sync activities`

Show when each category of your data was last updated on Trakt.

```bash
trakt sync activities
```

Displays timestamps for movies, episodes, shows, seasons, and overall last activity.

---

### `trakt sync history`

Your full watch history across all media types.

```bash
trakt sync history
trakt sync history --type movies --limit 50
trakt sync history --type episodes --page 2
```

Output columns: `ID`, `Watched At`, `Type`, `Title`, `Ep`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | _(all)_ | `movies`, `shows`, `seasons`, or `episodes` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `20` | Results per page |

---

### `trakt sync watched movies|shows`

Everything you've watched, deduplicated. Shows play counts and last watched date.

```bash
trakt sync watched movies
trakt sync watched shows
```

Output columns: `#`, `Plays`, `Last Watched`, `Title`, `Slug`

---

### `trakt sync collection movies|shows`

Your collected movies or shows.

```bash
trakt sync collection movies
trakt sync collection shows
```

Movie output columns: `#`, `Collected`, `Title`, `Year`, `Slug`
Show output columns: `#`, `Last Collected`, `Title`, `Seasons`, `Episodes`, `Slug`

---

### `trakt sync ratings`

Your ratings across movies, shows, seasons, and episodes.

```bash
trakt sync ratings
trakt sync ratings --type movies
trakt sync ratings --type shows --rating 10
```

Output columns: `Rating`, `Type`, `Title`, `Ep`, `Rated`, `Slug`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | `all` | `movies`, `shows`, `seasons`, `episodes`, or `all` |
| `--rating` | _(any)_ | Filter to a specific rating (1–10) |

---

### `trakt sync watchlist`

Your watchlist.

```bash
trakt sync watchlist
trakt sync watchlist --type movies
trakt sync watchlist --sort-by title --sort-how asc
```

Output columns: `Rank`, `Type`, `Title`, `Ep`, `Added`, `Notes`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | `all` | `all`, `movies`, `shows`, `seasons`, or `episodes` |
| `--sort-by` | `rank` | `rank`, `added`, `title`, `released`, `runtime`, `popularity`, `percentage`, `votes` |
| `--sort-how` | `asc` | `asc` or `desc` |
| `--page` / `-p` | _(none)_ | Page number |
| `--limit` / `-n` | _(none)_ | Results per page |

---

### `trakt sync playback`

Paused playback progress — movies or episodes you started but didn't finish.

```bash
trakt sync playback
trakt sync playback --type movies
```

Output columns: `ID`, `Progress`, `Type`, `Title`, `Ep`, `Paused At`

| Option | Default | Description |
|--------|---------|-------------|
| `--type` | _(all)_ | `movies` or `episodes` |
| `--page` / `-p` | `1` | Page number |
| `--limit` / `-n` | `10` | Results per page |

---

### `trakt sync remove-playback ID`

Delete a paused playback entry by its Trakt ID.

```bash
trakt sync remove-playback 123456
```

---

### `trakt sync add-history TYPE SLUG`

Mark a movie or entire show as watched.

```bash
trakt sync add-history movie the-dark-knight-2008
trakt sync add-history show breaking-bad
trakt sync add-history movie the-dark-knight-2008 --watched-at 2026-01-15T20:00:00Z
```

Displays a summary of added, updated, and existing entries.

| Option | Description |
|--------|-------------|
| `--watched-at` | When it was watched (ISO 8601). Defaults to now. |

---

### `trakt sync remove-history IDS...`

Remove specific history entries by their Trakt history IDs. IDs can be obtained from `trakt sync history`.

```bash
trakt sync remove-history 111 222 333
```

Displays a summary of removed entries.

---

### `trakt sync rate TYPE SLUG RATING`

Rate a movie or show on a 1–10 scale.

```bash
trakt sync rate movie the-dark-knight-2008 10
trakt sync rate show breaking-bad 10
```

`RATING` must be an integer from 1 to 10.

---

### `trakt sync unrate TYPE SLUG`

Remove your rating from a movie or show.

```bash
trakt sync unrate movie the-dark-knight-2008
trakt sync unrate show breaking-bad
```

---

### `trakt sync watchlist-add TYPE SLUG`

Add a movie or show to your watchlist.

```bash
trakt sync watchlist-add movie dune-part-two-2024
trakt sync watchlist-add show severance --notes "Everyone recommends this"
```

| Option | Description |
|--------|-------------|
| `--notes` | Optional note for the watchlist entry |

---

### `trakt sync watchlist-remove TYPE SLUG`

Remove a movie or show from your watchlist.

```bash
trakt sync watchlist-remove movie dune-part-two-2024
```

---

## `trakt users` — Users

User profiles, stats, social data, and hidden items. Most read commands default to `--user me` and can optionally target any public user.

```bash
trakt users --help
```

### `trakt users profile`

View a user's profile — username, name, VIP status, join date, location, and bio.

```bash
trakt users profile
trakt users profile --user johndoe
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users stats`

Aggregate watch stats — movies watched, plays, minutes, shows, episodes, collection counts, and social counts.

```bash
trakt users stats
trakt users stats --user johndoe
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users settings`

Your account settings — timezone, date format, connected services, and watchlist limit. Requires auth.

```bash
trakt users settings
```

---

### `trakt users watching`

See what a user is currently watching, if anything.

```bash
trakt users watching
trakt users watching --user johndoe
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users history`

Watch history for a user.

```bash
trakt users history
trakt users history --user johndoe --type movies --limit 50
```

Output columns: `ID`, `Watched At`, `Type`, `Title`, `Ep`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |
| `--type` | | _(all)_ | `movies`, `shows`, `seasons`, or `episodes` |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `20` | Results per page |

---

### `trakt users ratings`

Ratings for a user.

```bash
trakt users ratings
trakt users ratings --user johndoe --type movies --rating 10
```

Output columns: `Rating`, `Type`, `Title`, `Ep`, `Rated`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |
| `--type` | | `all` | `movies`, `shows`, `seasons`, `episodes`, or `all` |
| `--rating` | | _(any)_ | Filter by a specific rating (1–10) |

---

### `trakt users watched movies|shows`

Everything a user has watched.

```bash
trakt users watched movies
trakt users watched shows --user johndoe
```

Output columns: `#`, `Plays`, `Last Watched`, `Title`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users lists`

Personal lists belonging to a user.

```bash
trakt users lists
trakt users lists --user johndoe
```

Output columns: `Name`, `Privacy`, `Items`, `Likes`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users list-items LIST_SLUG`

Items in a user's personal list.

```bash
trakt users list-items my-favorite-films
trakt users list-items my-favorite-films --user johndoe --limit 50
```

Output columns: `#`, `Type`, `Title`, `Ep`, `Notes`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `20` | Results per page |

---

### `trakt users followers`

List a user's followers.

```bash
trakt users followers
trakt users followers --user johndoe
```

Output columns: `Username`, `Name`, `VIP`, `Since`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users following`

List users that a user is following.

```bash
trakt users following
trakt users following --user johndoe
```

Output columns: `Username`, `Name`, `VIP`, `Since`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users friends`

List mutual follows (friends).

```bash
trakt users friends
trakt users friends --user johndoe
```

Output columns: `Username`, `Name`, `VIP`, `Since`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--user` | `-u` | `me` | Username or slug |

---

### `trakt users follow USERNAME`

Follow a user. Requires auth.

```bash
trakt users follow johndoe
```

---

### `trakt users unfollow USERNAME`

Unfollow a user. Requires auth.

```bash
trakt users unfollow johndoe
```

---

### `trakt users hidden SECTION`

Your hidden items for a given section. Requires auth.

```bash
trakt users hidden calendar
trakt users hidden progress_watched --limit 50
```

Valid sections: `calendar`, `progress_watched`, `progress_collected`, `progress_watched_reset`, `recommendations`, `comments`, `lists`, `movies`, `shows`, `seasons`, `users`

Output columns: `Type`, `Title`, `Hidden`, `Slug`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--page` | `-p` | `1` | Page number |
| `--limit` | `-n` | `20` | Results per page |

---

### `trakt users hide SECTION TYPE SLUG`

Hide a movie or show from a section. Requires auth.

```bash
trakt users hide calendar movie some-movie-2024
trakt users hide recommendations show lost
```

`SECTION` is any valid section name (see `users hidden` above).
`TYPE` is `movie` or `show`.

---

### `trakt users unhide SECTION TYPE SLUG`

Unhide a previously hidden item. Requires auth.

```bash
trakt users unhide calendar movie some-movie-2024
trakt users unhide recommendations show lost
```

---

## `trakt config` — Configuration

Manage stored credentials.

```bash
trakt config --help
```

### `trakt config set-key KEY`

Save an API key (Client ID) to `~/.config/trakt-cli/config.ini`.

```bash
trakt config set-key YOUR_CLIENT_ID
```

---

### `trakt config set-secret SECRET`

Save a client secret to `~/.config/trakt-cli/config.ini`. Required for the OAuth login flow.

```bash
trakt config set-secret YOUR_CLIENT_SECRET
```

---

## Pagination

Commands that return lists support `--page` and `--limit`. When there is more than one page of results, a footer is printed showing the current page, total pages, and total result count:

```
Page 1/443  2211 total results
```

---

## Project Structure

```
trakt_cli/
    __init__.py      # package marker
    __main__.py      # enables python -m trakt_cli
    config.py        # API key and token loading/saving
    api.py           # HTTP client wrapping the Trakt API
    output.py        # Rich-formatted tables and panels
    cli.py           # Click command definitions
pyproject.toml
traktapi.txt         # agent86 app credentials (gitignored)
```
