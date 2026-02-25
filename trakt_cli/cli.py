from __future__ import annotations

import sys
import time
from datetime import datetime, timezone, timedelta

import click
import httpx

from trakt_cli import api, config, output as out

_PERIODS = click.Choice(["daily", "weekly", "monthly", "all"])
_SYNC_TYPES_MEDIA = click.Choice(["movie", "show"])
_SYNC_RATING = click.IntRange(1, 10)
_COMMENT_SORT = click.Choice(["newest", "oldest", "likes", "replies", "highest", "lowest", "plays", "watched"])


def _make_client() -> api.TraktClient:
    key = config.load_api_key()
    if not key:
        out.print_error(
            "No API key found. Set TRAKT_API_KEY, run 'trakt config set-key KEY', "
            "or place traktapi.txt in the current directory."
        )
        sys.exit(1)
    token = config.load_token()
    if token:
        created_at = token.get("created_at", 0)
        expires_in = token.get("expires_in", 0)
        if time.time() > created_at + expires_in - 3600:
            refresh = token.get("refresh_token")
            client_secret = config.load_client_secret()
            if refresh and client_secret:
                try:
                    token = api.refresh_token(refresh, key, client_secret)
                    config.save_token(token)
                except httpx.HTTPStatusError:
                    config.clear_token()
                    out.console.print(
                        "[yellow]Session expired. Run 'trakt auth login' to re-authenticate.[/yellow]"
                    )
                    token = None
    access_token = token["access_token"] if token else None
    return api.TraktClient(key, access_token=access_token)


@click.group()
def cli() -> None:
    """Trakt.tv CLI — browse shows, movies, your sync data, and more."""


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def search(query: tuple[str, ...], page: int, limit: int) -> None:
    """Search for shows by title."""
    client = _make_client()
    query_str = " ".join(query)
    try:
        results, meta = client.search_shows(query_str, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    if not results:
        out.console.print("[dim]No results found.[/dim]")
        return
    out.print_search_results(results, meta)


@cli.command()
@click.argument("show_id")
def info(show_id: str) -> None:
    """Show detailed info for a show (slug, IMDB ID, or Trakt ID)."""
    client = _make_client()
    try:
        show, meta = client.get_show(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_show_info(show)


@cli.command()
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def trending(page: int, limit: int) -> None:
    """List currently trending shows."""
    client = _make_client()
    try:
        results, meta = client.trending_shows(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_trending_shows(results, meta)


@cli.command()
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def popular(page: int, limit: int) -> None:
    """List the most popular shows of all time."""
    client = _make_client()
    try:
        results, meta = client.popular_shows(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_popular_shows(results, meta)


@cli.command()
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def favorited(period: str, page: int, limit: int) -> None:
    """Most favorited shows for a time period."""
    client = _make_client()
    try:
        results, meta = client.favorited_shows(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "user_count", "Users")


@cli.command()
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def played(period: str, page: int, limit: int) -> None:
    """Most played shows (total play count) for a time period."""
    client = _make_client()
    try:
        results, meta = client.played_shows(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "play_count", "Plays")


@cli.command()
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def watched(period: str, page: int, limit: int) -> None:
    """Most watched shows (unique users) for a time period."""
    client = _make_client()
    try:
        results, meta = client.watched_shows(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "watcher_count", "Watchers")


@cli.command()
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def collected(period: str, page: int, limit: int) -> None:
    """Most collected shows (unique collectors) for a time period."""
    client = _make_client()
    try:
        results, meta = client.collected_shows(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "collector_count", "Collectors")


@cli.command()
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def anticipated(page: int, limit: int) -> None:
    """Most anticipated upcoming shows."""
    client = _make_client()
    try:
        results, meta = client.anticipated_shows(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "list_count", "Lists")


@cli.command()
@click.option(
    "-s", "--since",
    default=None,
    help="Start date (YYYY-MM-DD or YYYY-MM-DDTHH:00:00Z). Defaults to 24 hours ago.",
)
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def updates(since: str | None, page: int, limit: int) -> None:
    """Shows updated since a date (max 30 days ago)."""
    if since is None:
        dt = datetime.now(timezone.utc) - timedelta(days=1)
        since = dt.strftime("%Y-%m-%dT%H:00:00Z")
    client = _make_client()
    try:
        results, meta = client.updated_shows(start_date=since, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_updated_shows(results, meta)


_ID_TYPES = click.Choice(["imdb", "tmdb", "tvdb", "trakt"])
_LOOKUP_TYPES = click.Choice(["movie", "show", "episode", "person", "list"])


@cli.command()
@click.argument("id_type", type=_ID_TYPES)
@click.argument("id_value")
@click.option("-t", "--type", "type_filter", type=_LOOKUP_TYPES, default=None,
              help="Restrict results to a single type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def lookup(id_type: str, id_value: str, type_filter: str | None, page: int, limit: int) -> None:
    """Look up an item by its IMDB, TMDB, TVDB, or Trakt ID."""
    client = _make_client()
    try:
        results, meta = client.lookup(id_type, id_value, type_filter=type_filter,
                                      page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_lookup_results(results, meta)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _calendar_options(fn):
    fn = click.option("-d", "--date", default=None,
                      help="Start date (YYYY-MM-DD). Defaults to today.")(fn)
    fn = click.option("-D", "--days", default=7, show_default=True,
                      help="Number of days to include.")(fn)
    return fn


@cli.group(name="calendar")
def calendar_cmd() -> None:
    """What's airing or releasing soon."""


@calendar_cmd.command("shows")
@_calendar_options
def cal_shows(date: str | None, days: int) -> None:
    """All episodes airing in a date range."""
    client = _make_client()
    try:
        results = client.calendar_shows(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_shows(results)


@calendar_cmd.command("new")
@_calendar_options
def cal_new(date: str | None, days: int) -> None:
    """New series premiering in a date range."""
    client = _make_client()
    try:
        results = client.calendar_new_shows(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_shows(results)


@calendar_cmd.command("premieres")
@_calendar_options
def cal_premieres(date: str | None, days: int) -> None:
    """Season premieres airing in a date range."""
    client = _make_client()
    try:
        results = client.calendar_premieres(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_shows(results)


@calendar_cmd.command("finales")
@_calendar_options
def cal_finales(date: str | None, days: int) -> None:
    """Season finales airing in a date range."""
    client = _make_client()
    try:
        results = client.calendar_finales(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_shows(results)


@calendar_cmd.command("movies")
@_calendar_options
def cal_movies(date: str | None, days: int) -> None:
    """Movies releasing in a date range."""
    client = _make_client()
    try:
        results = client.calendar_movies(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_movies(results)


@calendar_cmd.command("streaming")
@_calendar_options
def cal_streaming(date: str | None, days: int) -> None:
    """Movies hitting U.S. streaming in a date range."""
    client = _make_client()
    try:
        results = client.calendar_streaming(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_movies(results)


@calendar_cmd.command("dvd")
@_calendar_options
def cal_dvd(date: str | None, days: int) -> None:
    """Movies releasing on U.S. DVD in a date range."""
    client = _make_client()
    try:
        results = client.calendar_dvd(date or _today(), days)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_calendar_movies(results)


@cli.group(name="movies")
def movies_cmd() -> None:
    """Query movie data."""


@movies_cmd.command("search")
@click.argument("query", nargs=-1, required=True)
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_search(query: tuple[str, ...], page: int, limit: int) -> None:
    """Search for movies by title."""
    client = _make_client()
    try:
        results, meta = client.search_movies(" ".join(query), page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    if not results:
        out.console.print("[dim]No results found.[/dim]")
        return
    out.print_search_results(results, meta, item_key="movie")


@movies_cmd.command("info")
@click.argument("movie_id")
def movies_info(movie_id: str) -> None:
    """Show detailed info for a movie (slug, IMDB ID, or Trakt ID)."""
    client = _make_client()
    try:
        movie, _ = client.get_movie(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_movie_info(movie)


@movies_cmd.command("trending")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_trending(page: int, limit: int) -> None:
    """Most watched movies over the last 24 hours."""
    client = _make_client()
    try:
        results, meta = client.trending_movies(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_trending_shows(results, meta, item_key="movie")


@movies_cmd.command("popular")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_popular(page: int, limit: int) -> None:
    """Most popular movies of all time."""
    client = _make_client()
    try:
        results, meta = client.popular_movies(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_popular_shows(results, meta)


@movies_cmd.command("favorited")
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_favorited(period: str, page: int, limit: int) -> None:
    """Most favorited movies for a time period."""
    client = _make_client()
    try:
        results, meta = client.favorited_movies(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "user_count", "Users", item_key="movie")


@movies_cmd.command("played")
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_played(period: str, page: int, limit: int) -> None:
    """Most played movies (total play count) for a time period."""
    client = _make_client()
    try:
        results, meta = client.played_movies(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "play_count", "Plays", item_key="movie")


@movies_cmd.command("watched")
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_watched(period: str, page: int, limit: int) -> None:
    """Most watched movies (unique users) for a time period."""
    client = _make_client()
    try:
        results, meta = client.watched_movies(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "watcher_count", "Watchers", item_key="movie")


@movies_cmd.command("collected")
@click.option("-t", "--period", default="weekly", show_default=True, type=_PERIODS, help="Time period: daily, weekly, monthly, or all.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_collected(period: str, page: int, limit: int) -> None:
    """Most collected movies (unique collectors) for a time period."""
    client = _make_client()
    try:
        results, meta = client.collected_movies(period=period, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "collector_count", "Collectors", item_key="movie")


@movies_cmd.command("anticipated")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_anticipated(page: int, limit: int) -> None:
    """Most anticipated upcoming movies."""
    client = _make_client()
    try:
        results, meta = client.anticipated_movies(page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_shows_with_metric(results, meta, "list_count", "Lists", item_key="movie")


@movies_cmd.command("boxoffice")
def movies_boxoffice() -> None:
    """Top 10 U.S. box office movies from last weekend."""
    client = _make_client()
    try:
        results, _ = client.boxoffice_movies()
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_boxoffice(results)


@movies_cmd.command("updates")
@click.option("-s", "--since", default=None,
              help="Start date (YYYY-MM-DD or YYYY-MM-DDTHH:00:00Z). Defaults to 24 hours ago.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_updates(since: str | None, page: int, limit: int) -> None:
    """Movies updated since a date (max 30 days ago)."""
    if since is None:
        dt = datetime.now(timezone.utc) - timedelta(days=1)
        since = dt.strftime("%Y-%m-%dT%H:00:00Z")
    client = _make_client()
    try:
        results, meta = client.updated_movies(start_date=since, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_updated_shows(results, meta, item_key="movie")


@movies_cmd.command("people")
@click.argument("movie_id")
def movies_people(movie_id: str) -> None:
    """Cast and crew for a movie."""
    client = _make_client()
    try:
        data = client.movie_people(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_people(data, has_episode_count=False)


@movies_cmd.command("related")
@click.argument("movie_id")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_related(movie_id: str, page: int, limit: int) -> None:
    """Movies related to a given movie."""
    client = _make_client()
    try:
        results, meta = client.movie_related(movie_id, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_popular_shows(results, meta)


@movies_cmd.command("ratings")
@click.argument("movie_id")
def movies_ratings(movie_id: str) -> None:
    """Rating distribution for a movie."""
    client = _make_client()
    try:
        data = client.movie_ratings(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_ratings(data)


@movies_cmd.command("stats")
@click.argument("movie_id")
def movies_stats(movie_id: str) -> None:
    """Play, collect, and engagement stats for a movie."""
    client = _make_client()
    try:
        data = client.movie_stats(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_stats(data)


@movies_cmd.command("aliases")
@click.argument("movie_id")
def movies_aliases(movie_id: str) -> None:
    """Alternate titles for a movie by country."""
    client = _make_client()
    try:
        data = client.movie_aliases(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_aliases(data)


@movies_cmd.command("watching")
@click.argument("movie_id")
def movies_watching(movie_id: str) -> None:
    """Users watching a movie right now."""
    client = _make_client()
    try:
        data = client.movie_watching(movie_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_watching(data)


@movies_cmd.command("comments")
@click.argument("movie_id")
@click.option("--sort", default="newest", show_default=True, type=_COMMENT_SORT, help="Sort order.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def movies_comments(movie_id: str, sort: str, page: int, limit: int) -> None:
    """Comments on a movie."""
    client = _make_client()
    try:
        results, meta = client.movie_comments(movie_id, sort=sort, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_comments(results, meta)


# ---------------------------------------------------------------------------
# Show sub-resources
# ---------------------------------------------------------------------------

@cli.group(name="show")
def show_cmd() -> None:
    """Sub-resources for a specific show."""


@show_cmd.command("seasons")
@click.argument("show_id")
def show_seasons(show_id: str) -> None:
    """List all seasons for a show."""
    client = _make_client()
    try:
        data = client.show_seasons(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_seasons(data)


@show_cmd.command("episodes")
@click.argument("show_id")
@click.argument("season", type=int)
def show_episodes(show_id: str, season: int) -> None:
    """List episodes in a season."""
    client = _make_client()
    try:
        data = client.show_episodes(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_episodes(data)


@show_cmd.command("people")
@click.argument("show_id")
def show_people(show_id: str) -> None:
    """Cast and crew for a show."""
    client = _make_client()
    try:
        data = client.show_people(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_people(data, has_episode_count=True)


@show_cmd.command("related")
@click.argument("show_id")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def show_related(show_id: str, page: int, limit: int) -> None:
    """Shows related to a given show."""
    client = _make_client()
    try:
        results, meta = client.show_related(show_id, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_popular_shows(results, meta)


@show_cmd.command("ratings")
@click.argument("show_id")
def show_ratings(show_id: str) -> None:
    """Rating distribution for a show."""
    client = _make_client()
    try:
        data = client.show_ratings(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_ratings(data)


@show_cmd.command("stats")
@click.argument("show_id")
def show_stats(show_id: str) -> None:
    """Play, collect, and engagement stats for a show."""
    client = _make_client()
    try:
        data = client.show_stats(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_stats(data)


@show_cmd.command("aliases")
@click.argument("show_id")
def show_aliases(show_id: str) -> None:
    """Alternate titles for a show by country."""
    client = _make_client()
    try:
        data = client.show_aliases(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_aliases(data)


@show_cmd.command("watching")
@click.argument("show_id")
def show_watching(show_id: str) -> None:
    """Users watching a show right now."""
    client = _make_client()
    try:
        data = client.show_watching(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_watching(data)


@show_cmd.command("comments")
@click.argument("show_id")
@click.option("--sort", default="newest", show_default=True, type=_COMMENT_SORT, help="Sort order.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def show_comments(show_id: str, sort: str, page: int, limit: int) -> None:
    """Comments on a show."""
    client = _make_client()
    try:
        results, meta = client.show_comments(show_id, sort=sort, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_comments(results, meta)


@show_cmd.command("next")
@click.argument("show_id")
def show_next(show_id: str) -> None:
    """Next episode scheduled to air."""
    client = _make_client()
    try:
        data = client.show_next_episode(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_episode_summary(data, "next")


@show_cmd.command("last")
@click.argument("show_id")
def show_last(show_id: str) -> None:
    """Most recently aired episode."""
    client = _make_client()
    try:
        data = client.show_last_episode(show_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_episode_summary(data, "last")


@show_cmd.command("episode")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
def show_episode(show_id: str, season: int, number: int) -> None:
    """Detailed info for a specific episode."""
    client = _make_client()
    try:
        data = client.episode_info(show_id, season, number)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_episode_info(data)


@show_cmd.command("episode-people")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
def show_episode_people(show_id: str, season: int, number: int) -> None:
    """Cast and crew for a specific episode."""
    client = _make_client()
    try:
        data = client.episode_people(show_id, season, number)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_people(data, has_episode_count=False)


@show_cmd.command("episode-ratings")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
def show_episode_ratings(show_id: str, season: int, number: int) -> None:
    """Rating distribution for a specific episode."""
    client = _make_client()
    try:
        data = client.episode_ratings(show_id, season, number)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_ratings(data)


@show_cmd.command("episode-stats")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
def show_episode_stats(show_id: str, season: int, number: int) -> None:
    """Play, collect, and engagement stats for a specific episode."""
    client = _make_client()
    try:
        data = client.episode_stats(show_id, season, number)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_stats(data)


@show_cmd.command("episode-watching")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
def show_episode_watching(show_id: str, season: int, number: int) -> None:
    """Users watching a specific episode right now."""
    client = _make_client()
    try:
        data = client.episode_watching(show_id, season, number)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_watching(data)


@show_cmd.command("episode-comments")
@click.argument("show_id")
@click.argument("season", type=int)
@click.argument("number", type=int)
@click.option("--sort", default="newest", show_default=True, type=_COMMENT_SORT, help="Sort order.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def show_episode_comments(show_id: str, season: int, number: int, sort: str, page: int, limit: int) -> None:
    """Comments on a specific episode."""
    client = _make_client()
    try:
        results, meta = client.episode_comments(show_id, season, number, sort=sort, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_comments(results, meta)


@show_cmd.command("season-info")
@click.argument("show_id")
@click.argument("season", type=int)
def show_season_info(show_id: str, season: int) -> None:
    """Detailed info for a specific season."""
    client = _make_client()
    try:
        data = client.season_info(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_season_info(data)


@show_cmd.command("season-people")
@click.argument("show_id")
@click.argument("season", type=int)
def show_season_people(show_id: str, season: int) -> None:
    """Cast and crew for a specific season."""
    client = _make_client()
    try:
        data = client.season_people(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_people(data, has_episode_count=True)


@show_cmd.command("season-ratings")
@click.argument("show_id")
@click.argument("season", type=int)
def show_season_ratings(show_id: str, season: int) -> None:
    """Rating distribution for a specific season."""
    client = _make_client()
    try:
        data = client.season_ratings(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_ratings(data)


@show_cmd.command("season-stats")
@click.argument("show_id")
@click.argument("season", type=int)
def show_season_stats(show_id: str, season: int) -> None:
    """Play, collect, and engagement stats for a specific season."""
    client = _make_client()
    try:
        data = client.season_stats(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_stats(data)


@show_cmd.command("season-watching")
@click.argument("show_id")
@click.argument("season", type=int)
def show_season_watching(show_id: str, season: int) -> None:
    """Users watching a specific season right now."""
    client = _make_client()
    try:
        data = client.season_watching(show_id, season)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_watching(data)


@show_cmd.command("season-comments")
@click.argument("show_id")
@click.argument("season", type=int)
@click.option("--sort", default="newest", show_default=True, type=_COMMENT_SORT, help="Sort order.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def show_season_comments(show_id: str, season: int, sort: str, page: int, limit: int) -> None:
    """Comments on a specific season."""
    client = _make_client()
    try:
        results, meta = client.season_comments(show_id, season, sort=sort, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_comments(results, meta)


@show_cmd.command("progress")
@click.argument("show_id")
@click.option("--specials", is_flag=True, default=False, help="Include specials (season 0).")
@click.option("--hidden", is_flag=True, default=False, help="Include hidden seasons.")
def show_progress(show_id: str, specials: bool, hidden: bool) -> None:
    """Your watched progress for a show (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        data = client.show_watched_progress(show_id, hidden=hidden, specials=specials)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_show_progress(data, mode="watched")


@show_cmd.command("collected-progress")
@click.argument("show_id")
@click.option("--specials", is_flag=True, default=False, help="Include specials (season 0).")
@click.option("--hidden", is_flag=True, default=False, help="Include hidden seasons.")
def show_collected_progress(show_id: str, specials: bool, hidden: bool) -> None:
    """Your collection progress for a show (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        data = client.show_collection_progress(show_id, hidden=hidden, specials=specials)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_show_progress(data, mode="collection")


@cli.group(name="people")
def people_cmd() -> None:
    """Look up people and their credits."""


@people_cmd.command("info")
@click.argument("person_id")
def people_info(person_id: str) -> None:
    """Detailed info for a person (slug, IMDB ID, or Trakt ID)."""
    client = _make_client()
    try:
        data = client.person_info(person_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_person_info(data)


@people_cmd.command("movies")
@click.argument("person_id")
def people_movies(person_id: str) -> None:
    """Movie credits for a person."""
    client = _make_client()
    try:
        data = client.person_movies(person_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_person_credits(data, media_type="movies")


@people_cmd.command("shows")
@click.argument("person_id")
def people_shows(person_id: str) -> None:
    """Show credits for a person."""
    client = _make_client()
    try:
        data = client.person_shows(person_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_person_credits(data, media_type="shows")


_LIST_TYPE = click.Choice(["personal", "official"])
_LIST_ITEM_TYPE = click.Choice(["movie", "show", "season", "episode", "person"])


@cli.group(name="lists")
def lists_cmd() -> None:
    """Browse public Trakt lists."""


@lists_cmd.command("trending")
@click.option("--type", "list_type", default="personal", show_default=True, type=_LIST_TYPE, help="List type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def lists_trending(list_type: str, page: int, limit: int) -> None:
    """Lists with the most likes and comments over the last 7 days."""
    client = _make_client()
    try:
        results, meta = client.lists_trending(list_type, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_public_lists(results, meta)


@lists_cmd.command("popular")
@click.option("--type", "list_type", default="personal", show_default=True, type=_LIST_TYPE, help="List type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def lists_popular(list_type: str, page: int, limit: int) -> None:
    """Most popular lists of all time."""
    client = _make_client()
    try:
        results, meta = client.lists_popular(list_type, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_public_lists(results, meta)


@lists_cmd.command("get")
@click.argument("list_id", type=int)
def lists_get(list_id: int) -> None:
    """Get a single list by Trakt ID (integer ID only — must be public)."""
    client = _make_client()
    try:
        data = client.list_get(list_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_list_info(data)


@lists_cmd.command("items")
@click.argument("list_id", type=int)
@click.option("--type", "item_type", default=None, type=_LIST_ITEM_TYPE, help="Filter by item type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def lists_items(list_id: int, item_type: str | None, page: int, limit: int) -> None:
    """Items on a public list."""
    client = _make_client()
    try:
        results, meta = client.list_items(list_id, item_type=item_type, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    out.print_user_list_items(results, meta)


@lists_cmd.command("like")
@click.argument("list_id", type=int)
def lists_like(list_id: int) -> None:
    """Like a public list (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        client.list_like(list_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]List liked.[/green]")


@lists_cmd.command("unlike")
@click.argument("list_id", type=int)
def lists_unlike(list_id: int) -> None:
    """Remove your like from a list (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        client.list_unlike(list_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]Like removed.[/green]")


@cli.group(name="comments")
def comments_cmd() -> None:
    """Read and write comments on movies, shows, episodes, and seasons."""


@comments_cmd.command("get")
@click.argument("comment_id", type=int)
def comments_get(comment_id: int) -> None:
    """Fetch a single comment by ID."""
    client = _make_client()
    try:
        data = client.comment_get(comment_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_comment(data)


_COMMENT_TYPES = click.Choice(["movie", "show", "season", "episode"])


@comments_cmd.command("post")
@click.argument("type", type=_COMMENT_TYPES)
@click.argument("id_or_slug")
@click.argument("text")
@click.option("--spoiler", is_flag=True, help="Mark as spoiler.")
def comments_post(type: str, id_or_slug: str, text: str, spoiler: bool) -> None:
    """Post a comment on a movie, show, season, or episode.

    ID_OR_SLUG is a Trakt slug (e.g. breaking-bad) or numeric Trakt ID.
    """
    client = _make_client()
    _require_auth(client)
    try:
        id_val = int(id_or_slug)
        ids: dict = {"trakt": id_val}
    except ValueError:
        ids = {"slug": id_or_slug}
    body = {"comment": text, "spoiler": spoiler, type: {"ids": ids}}
    try:
        result = client.comment_post(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_comment(result)


@comments_cmd.command("update")
@click.argument("comment_id", type=int)
@click.argument("text")
@click.option("--spoiler", is_flag=True, help="Mark as spoiler.")
def comments_update(comment_id: int, text: str, spoiler: bool) -> None:
    """Update your comment text."""
    client = _make_client()
    _require_auth(client)
    try:
        result = client.comment_update(comment_id, text, spoiler)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_comment(result)


@comments_cmd.command("delete")
@click.argument("comment_id", type=int)
def comments_delete(comment_id: int) -> None:
    """Delete your comment."""
    client = _make_client()
    _require_auth(client)
    try:
        client.comment_delete(comment_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]Comment deleted.[/green]")


@comments_cmd.command("replies")
@click.argument("comment_id", type=int)
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def comments_replies(comment_id: int, page: int, limit: int) -> None:
    """List replies to a comment."""
    client = _make_client()
    try:
        results, meta = client.comment_replies(comment_id, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_comments(results, meta)


@comments_cmd.command("reply")
@click.argument("comment_id", type=int)
@click.argument("text")
@click.option("--spoiler", is_flag=True, help="Mark as spoiler.")
def comments_reply(comment_id: int, text: str, spoiler: bool) -> None:
    """Post a reply to a comment."""
    client = _make_client()
    _require_auth(client)
    try:
        result = client.comment_reply(comment_id, text, spoiler)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_comment(result)


@comments_cmd.command("like")
@click.argument("comment_id", type=int)
def comments_like(comment_id: int) -> None:
    """Like a comment."""
    client = _make_client()
    _require_auth(client)
    try:
        client.comment_like(comment_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]Comment liked.[/green]")


@comments_cmd.command("unlike")
@click.argument("comment_id", type=int)
def comments_unlike(comment_id: int) -> None:
    """Unlike a comment."""
    client = _make_client()
    _require_auth(client)
    try:
        client.comment_unlike(comment_id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]Comment unliked.[/green]")


_HIDDEN_SECTIONS = click.Choice([
    "calendar", "progress_watched", "progress_collected", "progress_watched_reset",
    "recommendations", "comments", "lists", "movies", "shows", "seasons", "users",
])


@cli.group(name="users")
def users_cmd() -> None:
    """User profiles, stats, and social features."""


@users_cmd.command("settings")
def users_settings() -> None:
    """Your account settings (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        data = client.user_settings()
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_settings(data)


@users_cmd.command("profile")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_profile(username: str) -> None:
    """View a user's profile."""
    client = _make_client()
    try:
        data = client.user_profile(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_profile(data)


@users_cmd.command("stats")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_stats(username: str) -> None:
    """View a user's aggregate stats."""
    client = _make_client()
    try:
        data = client.user_stats(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_stats(data, username=username)


@users_cmd.command("watching")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_watching(username: str) -> None:
    """See what a user is currently watching."""
    client = _make_client()
    try:
        data = client.user_watching(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_watching(data)


@users_cmd.command("followers")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_followers(username: str) -> None:
    """List a user's followers."""
    client = _make_client()
    try:
        data = client.user_followers(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_network(data, "followers")


@users_cmd.command("following")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_following(username: str) -> None:
    """List users that a user is following."""
    client = _make_client()
    try:
        data = client.user_following(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_network(data, "following")


@users_cmd.command("friends")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_friends(username: str) -> None:
    """List mutual follows (friends)."""
    client = _make_client()
    try:
        data = client.user_friends(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_network(data, "friends")


@users_cmd.command("history")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
@click.option("--type", "type_filter",
              type=click.Choice(["movies", "shows", "seasons", "episodes"]),
              default=None, help="Filter by media type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=20, show_default=True, help="Results per page.")
def users_history(username: str, type_filter: str | None, page: int, limit: int) -> None:
    """Watch history for a user."""
    client = _make_client()
    try:
        results, meta = client.user_history(username, type=type_filter, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_history(results, meta)


@users_cmd.command("ratings")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
@click.option("--type", "type_filter",
              type=click.Choice(["movies", "shows", "seasons", "episodes", "all"]),
              default="all", show_default=True)
@click.option("--rating", type=_SYNC_RATING, default=None,
              help="Filter by a specific rating (1-10).")
def users_ratings(username: str, type_filter: str, rating: int | None) -> None:
    """Ratings for a user."""
    client = _make_client()
    try:
        results = client.user_ratings(username, type=type_filter, rating=rating)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_ratings(results)


@users_cmd.command("watched")
@click.argument("type", type=click.Choice(["movies", "shows"]))
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_watched(type: str, username: str) -> None:
    """Everything a user has watched."""
    client = _make_client()
    try:
        results = client.user_watched(username, type)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_watched(results, type)


@users_cmd.command("lists")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
def users_lists(username: str) -> None:
    """Personal lists for a user."""
    client = _make_client()
    try:
        data = client.user_lists(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_lists(data)


@users_cmd.command("list-items")
@click.argument("list_slug")
@click.option("-u", "--user", "username", default="me", show_default=True,
              help="Username or slug.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=20, show_default=True, help="Results per page.")
def users_list_items(list_slug: str, username: str, page: int, limit: int) -> None:
    """Items in a user's personal list."""
    client = _make_client()
    try:
        results, meta = client.user_list_items(username, list_slug, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_list_items(results, meta)


@users_cmd.command("hidden")
@click.argument("section", type=_HIDDEN_SECTIONS)
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=20, show_default=True, help="Results per page.")
def users_hidden(section: str, page: int, limit: int) -> None:
    """Your hidden items for a section (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        results, meta = client.user_hidden(section, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_user_hidden(results, meta)


@users_cmd.command("hide")
@click.argument("section", type=_HIDDEN_SECTIONS)
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
def users_hide(section: str, type: str, slug: str) -> None:
    """Hide a movie or show from a section (requires auth)."""
    client = _make_client()
    _require_auth(client)
    body = {f"{type}s": [{"ids": {"slug": slug}}]}
    try:
        result = client.user_hide(section, body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@users_cmd.command("unhide")
@click.argument("section", type=_HIDDEN_SECTIONS)
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
def users_unhide(section: str, type: str, slug: str) -> None:
    """Unhide a movie or show from a section (requires auth)."""
    client = _make_client()
    _require_auth(client)
    body = {f"{type}s": [{"ids": {"slug": slug}}]}
    try:
        result = client.user_unhide(section, body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@users_cmd.command("follow")
@click.argument("username")
def users_follow(username: str) -> None:
    """Follow a user (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        client.user_follow(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print(f"[green]Now following {username}.[/green]")


@users_cmd.command("unfollow")
@click.argument("username")
def users_unfollow(username: str) -> None:
    """Unfollow a user (requires auth)."""
    client = _make_client()
    _require_auth(client)
    try:
        client.user_unfollow(username)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print(f"[green]Unfollowed {username}.[/green]")


def _require_auth(client: api.TraktClient) -> None:
    if not client.is_authenticated:
        out.print_error("This command requires authentication. Run 'trakt auth login' first.")
        sys.exit(1)


def _handle_http(e: httpx.HTTPStatusError) -> None:
    if e.response.status_code == 401:
        out.print_error("Not authenticated. Run 'trakt auth login' first.")
    else:
        out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
    sys.exit(1)



@cli.group(name="sync")
def sync_cmd() -> None:
    """Your personal watch data (requires auth)."""


@sync_cmd.command("activities")
def sync_activities() -> None:
    """Show when each part of your data was last updated."""
    client = _make_client()
    _require_auth(client)
    try:
        data = client.sync_last_activities()
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_last_activities(data)


@sync_cmd.command("watched")
@click.argument("type", type=click.Choice(["movies", "shows"]))
def sync_watched(type: str) -> None:
    """List everything you've watched (movies or shows)."""
    client = _make_client()
    _require_auth(client)
    try:
        results = client.sync_watched(type)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_watched(results, type)


@sync_cmd.command("history")
@click.option("--type", "type_filter",
              type=click.Choice(["movies", "shows", "seasons", "episodes"]),
              default=None, help="Filter by media type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=20, show_default=True, help="Results per page.")
def sync_history(type_filter: str | None, page: int, limit: int) -> None:
    """Your full watch history."""
    client = _make_client()
    _require_auth(client)
    try:
        results, meta = client.sync_history(type=type_filter, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_history(results, meta)


@sync_cmd.command("ratings")
@click.option("--type", "type_filter",
              type=click.Choice(["movies", "shows", "seasons", "episodes", "all"]),
              default="all", show_default=True, help="Filter by media type.")
@click.option("--rating", type=_SYNC_RATING, default=None, help="Filter by a specific rating (1-10).")
def sync_ratings(type_filter: str, rating: int | None) -> None:
    """Your ratings."""
    client = _make_client()
    _require_auth(client)
    try:
        results = client.sync_ratings(type=type_filter, rating=rating)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_ratings(results)


@sync_cmd.command("watchlist")
@click.option("--type", "type_filter",
              type=click.Choice(["all", "movies", "shows", "seasons", "episodes"]),
              default="all", show_default=True, help="Filter by media type.")
@click.option("--sort-by", default="rank", show_default=True,
              type=click.Choice(["rank", "added", "title", "released", "runtime",
                                  "popularity", "percentage", "votes"]),
              help="Sort field.")
@click.option("--sort-how", default="asc", show_default=True,
              type=click.Choice(["asc", "desc"]), help="Sort direction.")
@click.option("-p", "--page", default=None, type=int, help="Page number.")
@click.option("-n", "--limit", default=None, type=int, help="Results per page.")
def sync_watchlist(type_filter: str, sort_by: str, sort_how: str,
                   page: int | None, limit: int | None) -> None:
    """Your watchlist."""
    client = _make_client()
    _require_auth(client)
    try:
        results, meta = client.sync_watchlist(type=type_filter, sort_by=sort_by,
                                               sort_how=sort_how, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_watchlist(results, meta)


@sync_cmd.command("collection")
@click.argument("type", type=click.Choice(["movies", "shows"]))
def sync_collection(type: str) -> None:
    """Your collected movies or shows."""
    client = _make_client()
    _require_auth(client)
    try:
        results = client.sync_collection(type)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_collection(results, type)


@sync_cmd.command("playback")
@click.option("--type", "type_filter",
              type=click.Choice(["movies", "episodes"]),
              default=None, help="Filter by media type.")
@click.option("-p", "--page", default=1, show_default=True, help="Page number.")
@click.option("-n", "--limit", default=10, show_default=True, help="Results per page.")
def sync_playback(type_filter: str | None, page: int, limit: int) -> None:
    """Paused playback progress."""
    client = _make_client()
    _require_auth(client)
    try:
        results, meta = client.sync_playback(type=type_filter, page=page, limit=limit)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_playback(results, meta)


@sync_cmd.command("remove-playback")
@click.argument("id", type=int)
def sync_remove_playback(id: int) -> None:
    """Delete a paused playback entry by its ID."""
    client = _make_client()
    _require_auth(client)
    try:
        client.sync_remove_playback(id)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print(f"[green]Playback {id} removed.[/green]")


@sync_cmd.command("add-history")
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
@click.option("--watched-at", default=None,
              help="When it was watched (ISO 8601). Defaults to now.")
def sync_add_history(type: str, slug: str, watched_at: str | None) -> None:
    """Mark a movie or show as watched."""
    client = _make_client()
    _require_auth(client)
    item: dict = {"ids": {"slug": slug}}
    if watched_at:
        item["watched_at"] = watched_at
    body = {f"{type}s": [item]}
    try:
        result = client.sync_add_history(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@sync_cmd.command("remove-history")
@click.argument("ids", type=int, nargs=-1, required=True)
def sync_remove_history(ids: tuple[int, ...]) -> None:
    """Remove history entries by their history IDs."""
    client = _make_client()
    _require_auth(client)
    body = {"ids": list(ids)}
    try:
        result = client.sync_remove_history(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@sync_cmd.command("rate")
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
@click.argument("rating", type=_SYNC_RATING)
def sync_rate(type: str, slug: str, rating: int) -> None:
    """Rate a movie or show (1-10)."""
    client = _make_client()
    _require_auth(client)
    body = {f"{type}s": [{"ids": {"slug": slug}, "rating": rating}]}
    try:
        result = client.sync_add_ratings(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@sync_cmd.command("unrate")
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
def sync_unrate(type: str, slug: str) -> None:
    """Remove a rating from a movie or show."""
    client = _make_client()
    _require_auth(client)
    body = {f"{type}s": [{"ids": {"slug": slug}}]}
    try:
        result = client.sync_remove_ratings(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@sync_cmd.command("watchlist-add")
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
@click.option("--notes", default=None, help="Optional note for this watchlist entry.")
def sync_watchlist_add(type: str, slug: str, notes: str | None) -> None:
    """Add a movie or show to your watchlist."""
    client = _make_client()
    _require_auth(client)
    item: dict = {"ids": {"slug": slug}}
    if notes:
        item["notes"] = notes
    body = {f"{type}s": [item]}
    try:
        result = client.sync_add_watchlist(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@sync_cmd.command("watchlist-remove")
@click.argument("type", type=_SYNC_TYPES_MEDIA)
@click.argument("slug")
def sync_watchlist_remove(type: str, slug: str) -> None:
    """Remove a movie or show from your watchlist."""
    client = _make_client()
    _require_auth(client)
    body = {f"{type}s": [{"ids": {"slug": slug}}]}
    try:
        result = client.sync_remove_watchlist(body)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_sync_result(result)


@cli.group(name="recommendations")
def recommendations_cmd() -> None:
    """Personalized movie and show recommendations (requires auth)."""


@recommendations_cmd.command("movies")
@click.option("-n", "--limit", default=10, show_default=True, type=click.IntRange(1, 100),
              help="Number of results (max 100).")
@click.option("--ignore-collected", is_flag=True, default=False,
              help="Exclude movies you've already collected.")
@click.option("--ignore-watchlisted", is_flag=True, default=False,
              help="Exclude movies already on your watchlist.")
def rec_movies(limit: int, ignore_collected: bool, ignore_watchlisted: bool) -> None:
    """Personalized movie recommendations."""
    client = _make_client()
    _require_auth(client)
    try:
        results, _ = client.recommendations_movies(
            limit=limit,
            ignore_collected=ignore_collected,
            ignore_watchlisted=ignore_watchlisted,
        )
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_recommendations(results, item_key="movie")


@recommendations_cmd.command("shows")
@click.option("-n", "--limit", default=10, show_default=True, type=click.IntRange(1, 100),
              help="Number of results (max 100).")
@click.option("--ignore-collected", is_flag=True, default=False,
              help="Exclude shows you've already collected.")
@click.option("--ignore-watchlisted", is_flag=True, default=False,
              help="Exclude shows already on your watchlist.")
def rec_shows(limit: int, ignore_collected: bool, ignore_watchlisted: bool) -> None:
    """Personalized show recommendations."""
    client = _make_client()
    _require_auth(client)
    try:
        results, _ = client.recommendations_shows(
            limit=limit,
            ignore_collected=ignore_collected,
            ignore_watchlisted=ignore_watchlisted,
        )
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.print_recommendations(results, item_key="show")


@recommendations_cmd.command("hide")
@click.argument("type", type=click.Choice(["movie", "show"]))
@click.argument("slug")
def rec_hide(type: str, slug: str) -> None:
    """Hide a movie or show from future recommendations."""
    client = _make_client()
    _require_auth(client)
    try:
        if type == "movie":
            client.recommendations_hide_movie(slug)
        else:
            client.recommendations_hide_show(slug)
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print(f"[green]{slug}[/green] hidden from recommendations.")


def _handle_checkin_409(e: httpx.HTTPStatusError) -> None:
    expires_at = e.response.json().get("expires_at", "")
    expires_fmt = expires_at[:16].replace("T", " ") + " UTC" if expires_at else "unknown"
    out.print_error(f"Already checked in. Try again after {expires_fmt}.")
    sys.exit(1)


@cli.group(name="checkin")
def checkin_cmd() -> None:
    """Check in to what you're watching right now (requires auth)."""


@checkin_cmd.command("movie")
@click.argument("slug")
@click.option("--message", default=None, help="Message for social sharing.")
def checkin_movie(slug: str, message: str | None) -> None:
    """Check in to a movie by slug."""
    client = _make_client()
    _require_auth(client)
    body: dict = {"movie": {"ids": {"slug": slug}}}
    if message:
        body["message"] = message
    try:
        result = client.checkin(body)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            _handle_checkin_409(e)
        else:
            _handle_http(e)
    out.print_checkin_result(result)


@checkin_cmd.command("episode")
@click.argument("show_slug")
@click.argument("season", type=int)
@click.argument("number", type=int)
@click.option("--message", default=None, help="Message for social sharing.")
def checkin_episode(show_slug: str, season: int, number: int, message: str | None) -> None:
    """Check in to an episode (SHOW_SLUG SEASON EPISODE)."""
    client = _make_client()
    _require_auth(client)
    body: dict = {
        "show": {"ids": {"slug": show_slug}},
        "episode": {"season": season, "number": number},
    }
    if message:
        body["message"] = message
    try:
        result = client.checkin(body)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            _handle_checkin_409(e)
        else:
            _handle_http(e)
    out.print_checkin_result(result)


@checkin_cmd.command("delete")
def checkin_delete() -> None:
    """Remove any active checkin."""
    client = _make_client()
    _require_auth(client)
    try:
        client.checkin_delete()
    except httpx.HTTPStatusError as e:
        _handle_http(e)
    out.console.print("[green]Active checkin removed.[/green]")


@cli.group(name="auth")
def auth_cmd() -> None:
    """Authenticate with Trakt via Device OAuth."""


@auth_cmd.command("login")
def auth_login() -> None:
    """Authenticate via Trakt Device OAuth flow."""
    client_id = config.load_api_key()
    if not client_id:
        out.print_error("No client ID found. Set TRAKT_API_KEY or place traktapi.txt in the current directory.")
        sys.exit(1)
    client_secret = config.load_client_secret()
    if not client_secret:
        out.print_error("No client secret found. Set TRAKT_CLIENT_SECRET or place traktapi.txt in the current directory.")
        sys.exit(1)

    try:
        code_data = api.device_code(client_id)
    except httpx.HTTPStatusError as e:
        out.print_error(f"Failed to get device code: HTTP {e.response.status_code}")
        sys.exit(1)

    device_code_value = code_data["device_code"]
    user_code = code_data["user_code"]
    verification_url = code_data["verification_url"]
    expires_in = code_data["expires_in"]
    interval = code_data["interval"]

    out.console.print(f"Open: [bold]{verification_url}[/bold]")
    out.console.print(f"Enter code: [bold cyan]{user_code}[/bold cyan]")
    out.console.print("Waiting for authorization...", end="")

    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token_data = api.device_token(device_code_value, client_id, client_secret)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 410:
                out.console.print()
                out.print_error("Code expired. Run 'trakt auth login' again.")
            elif status == 418:
                out.console.print()
                out.print_error("Authorization denied.")
            elif status == 429:
                interval *= 2
                out.console.print(".", end="")
                continue
            else:
                out.console.print()
                out.print_error(f"HTTP {status}: {e.response.text}")
            sys.exit(1)

        if token_data is None:
            out.console.print(".", end="")
            continue

        config.save_token(token_data)
        config.save_client_secret(client_secret)
        out.console.print()
        out.console.print("[green]Logged in successfully.[/green]")
        return

    out.console.print()
    out.print_error("Timed out waiting for authorization.")
    sys.exit(1)


@auth_cmd.command("status")
def auth_status() -> None:
    """Show current authentication status."""
    token = config.load_token()
    if not token:
        out.console.print("[dim]Not logged in.[/dim]")
        return
    created_at = token.get("created_at", 0)
    expires_in = token.get("expires_in", 0)
    expiry = datetime.fromtimestamp(created_at + expires_in, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    if now >= expiry:
        out.console.print("[yellow]Token expired.[/yellow] Run 'trakt auth login' to re-authenticate.")
    else:
        out.console.print(f"[green]Logged in.[/green] Token expires {expiry.strftime('%Y-%m-%d %H:%M UTC')}.")


@auth_cmd.command("refresh")
def auth_refresh() -> None:
    """Manually refresh the access token using the stored refresh token."""
    token = config.load_token()
    if not token or not token.get("refresh_token"):
        out.print_error("No refresh token stored. Run 'trakt auth login' first.")
        sys.exit(1)
    client_id = config.load_api_key()
    client_secret = config.load_client_secret()
    if not client_id or not client_secret:
        out.print_error("Client ID or secret missing. Cannot refresh token.")
        sys.exit(1)
    try:
        new_token = api.refresh_token(token["refresh_token"], client_id, client_secret)
        config.save_token(new_token)
        out.console.print("[green]Token refreshed successfully.[/green]")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            config.clear_token()
            out.print_error("Refresh token is invalid or expired. Run 'trakt auth login' again.")
        else:
            out.print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)


@auth_cmd.command("logout")
def auth_logout() -> None:
    """Clear stored authentication token."""
    config.clear_token()
    out.console.print("[green]Logged out.[/green]")


@cli.group(name="config")
def config_cmd() -> None:
    """Manage CLI configuration."""


@config_cmd.command("set-key")
@click.argument("key")
def set_key(key: str) -> None:
    """Save an API key to ~/.config/trakt-cli/config.ini."""
    config.save_api_key(key)
    out.console.print("[green]API key saved.[/green]")


@config_cmd.command("set-secret")
@click.argument("secret")
def set_secret(secret: str) -> None:
    """Save a client secret to ~/.config/trakt-cli/config.ini."""
    config.save_client_secret(secret)
    out.console.print("[green]Client secret saved.[/green]")
