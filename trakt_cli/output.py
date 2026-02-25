from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def print_error(message: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {message}")


def _pagination_footer(meta: dict) -> str | None:
    page = meta.get("page")
    page_count = meta.get("page_count")
    item_count = meta.get("item_count")
    if page_count and page_count > 1:
        parts = [f"Page {page}/{page_count}"]
        if item_count:
            parts.append(f"{item_count} total results")
        return "  ".join(parts)
    return None


def print_lookup_results(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]No results found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Type", width=8)
    table.add_column("Title / Name")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Detail", style="dim")
    table.add_column("Slug / ID", style="dim")

    for item in results:
        result_type = item.get("type", "")

        if result_type == "movie":
            obj = item.get("movie", {})
            ids = obj.get("ids", {})
            table.add_row("movie", obj.get("title", "—"), str(obj.get("year") or "—"),
                          f"imdb:{ids.get('imdb', '—')}", ids.get("slug", "—"))

        elif result_type == "show":
            obj = item.get("show", {})
            ids = obj.get("ids", {})
            table.add_row("show", obj.get("title", "—"), str(obj.get("year") or "—"),
                          f"imdb:{ids.get('imdb', '—')}", ids.get("slug", "—"))

        elif result_type == "episode":
            ep = item.get("episode", {})
            show = item.get("show", {})
            s, e = ep.get("season", "?"), ep.get("number", "?")
            ids = ep.get("ids", {})
            table.add_row("episode", show.get("title", "—"), str(show.get("year") or "—"),
                          f"S{s:02d}E{e:02d}  \"{ep.get('title') or ''}\"",
                          str(ids.get("trakt", "—")))

        elif result_type == "person":
            obj = item.get("person", {})
            ids = obj.get("ids", {})
            table.add_row("person", obj.get("name", "—"), "",
                          f"imdb:{ids.get('imdb', '—')}", ids.get("slug", "—"))

        elif result_type == "list":
            obj = item.get("list", {})
            ids = obj.get("ids", {})
            table.add_row("list", obj.get("name", "—"), "",
                          f"by {obj.get('username', '—')}", ids.get("slug", "—"))

        else:
            table.add_row(result_type, "—", "—", "—", "—")

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_search_results(results: list[dict], meta: dict, item_key: str = "show") -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Score", width=7, justify="right")
    table.add_column("Slug")

    for i, item in enumerate(results, 1):
        entry = item.get(item_key, {})
        ids = entry.get("ids", {})
        score = item.get("score")
        score_str = f"{score:.1f}" if score is not None else "—"
        table.add_row(
            str(i),
            entry.get("title", "—"),
            str(entry.get("year") or "—"),
            score_str,
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_movie_info(movie: dict) -> None:
    ids = movie.get("ids", {})
    title = movie.get("title", "Unknown")
    year = movie.get("year", "")

    lines: list[str] = []

    def add(label: str, value: object) -> None:
        if value is not None and value != "" and value != []:
            lines.append(f"[bold]{label}:[/bold] {value}")

    add("Status", movie.get("status"))
    add("Released", movie.get("released"))
    add("Runtime", f"{movie['runtime']} min" if movie.get("runtime") else None)
    add("Certification", movie.get("certification"))
    add("Country", movie.get("country", "").upper() or None)

    languages = movie.get("languages")
    if languages:
        add("Languages", ", ".join(l.upper() for l in languages))

    add("Rating", f"{movie['rating']:.1f}/10  ({movie['votes']:,} votes)"
        if movie.get("rating") is not None and movie.get("votes") is not None else None)

    genres = movie.get("genres")
    if genres:
        add("Genres", ", ".join(genres))

    add("Tagline", movie.get("tagline"))
    add("Homepage", movie.get("homepage"))
    add("Trailer", movie.get("trailer"))
    add("Trakt slug", ids.get("slug"))
    add("IMDB", ids.get("imdb"))
    add("TMDB", ids.get("tmdb"))

    overview = movie.get("overview", "")
    if overview:
        lines.append("")
        lines.append(overview)

    header = f"[bold]{title}[/bold]" + (f"  [dim]({year})[/dim]" if year else "")
    console.print(Panel("\n".join(lines), title=header, expand=False))


def print_boxoffice(results: list[dict]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Revenue (USD)", justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug")

    for i, item in enumerate(results, 1):
        movie = item.get("movie", {})
        ids = movie.get("ids", {})
        revenue = item.get("revenue")
        revenue_str = f"${revenue:,}" if isinstance(revenue, int) else "—"
        table.add_row(
            str(i),
            revenue_str,
            movie.get("title", "—"),
            str(movie.get("year") or "—"),
            ids.get("slug", "—"),
        )

    console.print(table)


def print_show_info(show: dict) -> None:
    ids = show.get("ids", {})
    title = show.get("title", "Unknown")
    year = show.get("year", "")

    lines: list[str] = []

    def add(label: str, value: object) -> None:
        if value is not None and value != "" and value != []:
            lines.append(f"[bold]{label}:[/bold] {value}")

    add("Status", show.get("status"))
    add("Network", show.get("network"))
    add("Country", show.get("country", "").upper() or None)
    add("Language", show.get("language", "").upper() or None)
    add("Runtime", f"{show['runtime']} min" if show.get("runtime") else None)
    add("Rating", f"{show['rating']:.1f}/10  ({show['votes']:,} votes)"
        if show.get("rating") is not None and show.get("votes") is not None else None)
    add("Aired episodes", show.get("aired_episodes"))

    genres = show.get("genres")
    if genres:
        add("Genres", ", ".join(genres))

    add("Trakt slug", ids.get("slug"))
    add("IMDB", ids.get("imdb"))
    add("TMDB", ids.get("tmdb"))
    add("TVDB", ids.get("tvdb"))

    overview = show.get("overview", "")
    if overview:
        lines.append("")
        lines.append(overview)

    header = f"[bold]{title}[/bold]" + (f"  [dim]({year})[/dim]" if year else "")
    console.print(Panel("\n".join(lines), title=header, expand=False))


def print_trending_shows(results: list[dict], meta: dict, item_key: str = "show") -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Watchers", width=9, justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug")

    for i, item in enumerate(results, 1):
        entry = item.get(item_key, {})
        ids = entry.get("ids", {})
        table.add_row(
            str(i),
            str(item.get("watchers", "—")),
            entry.get("title", "—"),
            str(entry.get("year") or "—"),
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_shows_with_metric(
    results: list[dict],
    meta: dict,
    metric_key: str,
    metric_label: str,
    item_key: str = "show",
) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column(metric_label, justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug")

    for i, item in enumerate(results, 1):
        entry = item.get(item_key, {})
        ids = entry.get("ids", {})
        value = item.get(metric_key)
        value_str = f"{value:,}" if isinstance(value, int) else str(value) if value is not None else "—"
        table.add_row(
            str(i),
            value_str,
            entry.get("title", "—"),
            str(entry.get("year") or "—"),
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_updated_shows(results: list[dict], meta: dict, item_key: str = "show") -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Updated At")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug")

    for i, item in enumerate(results, 1):
        entry = item.get(item_key, {})
        ids = entry.get("ids", {})
        updated_at = item.get("updated_at", "—")
        # Trim to date+time without sub-seconds: 2014-09-22T21:56:03.000Z → 2014-09-22 21:56
        if updated_at and "T" in updated_at:
            updated_at = updated_at[:16].replace("T", " ")
        table.add_row(
            str(i),
            updated_at,
            entry.get("title", "—"),
            str(entry.get("year") or "—"),
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_popular_shows(results: list[dict], meta: dict) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug")

    for i, show in enumerate(results, 1):
        ids = show.get("ids", {})
        table.add_row(
            str(i),
            show.get("title", "—"),
            str(show.get("year") or "—"),
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def _fmt_date_header(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %b %d").replace(" 0", " ")
    except ValueError:
        return date_str


def print_calendar_shows(results: list[dict]) -> None:
    if not results:
        console.print("[dim]No episodes found.[/dim]")
        return

    groups: dict[str, list[dict]] = defaultdict(list)
    for item in results:
        fa = item.get("first_aired", "") or ""
        date = fa[:10] if fa else "Unknown"
        groups[date].append(item)

    for date in sorted(groups):
        console.print(f"\n[bold cyan]{_fmt_date_header(date)}[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Show", style="bold")
        table.add_column("Ep", style="dim", width=6, no_wrap=True)
        table.add_column("Episode Title")
        table.add_column("Time", justify="right", style="dim", width=9, no_wrap=True)

        for item in groups[date]:
            show = item.get("show", {})
            ep = item.get("episode", {})
            fa = item.get("first_aired", "") or ""
            s, e = ep.get("season", 0), ep.get("number", 0)
            ep_title = ep.get("title") or ""
            time_str = (fa[11:16] + " UTC") if len(fa) >= 16 else ""
            table.add_row(
                show.get("title", "—"),
                f"S{s:02d}E{e:02d}",
                f'"{ep_title}"' if ep_title else "",
                time_str,
            )
        console.print(table)


def print_calendar_movies(results: list[dict]) -> None:
    if not results:
        console.print("[dim]No movies found.[/dim]")
        return

    groups: dict[str, list[dict]] = defaultdict(list)
    for item in results:
        date = item.get("released", "Unknown") or "Unknown"
        groups[date].append(item)

    for date in sorted(groups):
        console.print(f"\n[bold cyan]{_fmt_date_header(date)}[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Title", style="bold")
        table.add_column("Year", justify="right", style="dim", no_wrap=True)
        table.add_column("Slug", style="dim")

        for item in groups[date]:
            movie = item.get("movie", {})
            ids = movie.get("ids", {})
            table.add_row(
                movie.get("title", "—"),
                str(movie.get("year") or "—"),
                ids.get("slug", "—"),
            )
        console.print(table)


# ---------------------------------------------------------------------------
# Sub-resource output (shared by shows and movies)
# ---------------------------------------------------------------------------

def print_seasons(seasons: list[dict]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Season", justify="right", width=7)
    table.add_column("Title")
    table.add_column("Episodes", justify="right", width=9)
    table.add_column("Aired", justify="right", width=7)
    table.add_column("Rating", justify="right", width=8)

    for s in seasons:
        num = s.get("number", "?")
        label = s.get("title") or (f"Season {num}" if num != 0 else "Specials")
        ep_count = s.get("episode_count")
        aired = s.get("aired_episodes")
        rating = s.get("rating")
        table.add_row(
            str(num),
            label,
            str(ep_count) if ep_count is not None else "—",
            str(aired) if aired is not None else "—",
            f"{rating:.1f}" if rating else "—",
        )
    console.print(table)


def print_episodes(episodes: list[dict]) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Ep", justify="right", width=4)
    table.add_column("Title")
    table.add_column("Trakt ID", justify="right", style="dim", width=10)

    for ep in episodes:
        ids = ep.get("ids", {})
        table.add_row(
            str(ep.get("number", "?")),
            ep.get("title") or "—",
            str(ids.get("trakt", "—")),
        )
    console.print(table)


def print_people(data: dict, has_episode_count: bool = True) -> None:
    cast = data.get("cast", [])
    crew = data.get("crew", {})

    if cast:
        console.print("\n[bold cyan]Cast[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Name")
        table.add_column("Characters")
        if has_episode_count:
            table.add_column("Eps", justify="right", width=5)
        table.add_column("Slug", style="dim")

        for member in cast[:20]:
            person = member.get("person", {})
            chars = ", ".join(member.get("characters") or [])
            ids = person.get("ids", {})
            row = [person.get("name", "—"), chars]
            if has_episode_count:
                ec = member.get("episode_count")
                row.append(str(ec) if ec is not None else "—")
            row.append(ids.get("slug", "—"))
            table.add_row(*row)
        console.print(table)

    key_depts = ["directing", "writing", "created by", "production"]
    for dept in key_depts:
        members = crew.get(dept, [])
        if not members:
            continue
        console.print(f"\n[bold cyan]{dept.title()}[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Name")
        table.add_column("Job")
        if has_episode_count:
            table.add_column("Eps", justify="right", width=5)
        table.add_column("Slug", style="dim")

        for member in members:
            person = member.get("person", {})
            jobs = ", ".join(member.get("jobs") or [])
            ids = person.get("ids", {})
            row = [person.get("name", "—"), jobs]
            if has_episode_count:
                ec = member.get("episode_count")
                row.append(str(ec) if ec is not None else "—")
            row.append(ids.get("slug", "—"))
            table.add_row(*row)
        console.print(table)


def print_ratings(data: dict) -> None:
    rating = data.get("rating", 0)
    votes = data.get("votes", 0)
    dist = data.get("distribution", {})

    console.print(f"\n[bold]{rating:.2f}[/bold] / 10   [dim]({votes:,} votes)[/dim]\n")

    max_count = max((dist.get(str(i), 0) for i in range(1, 11)), default=1) or 1
    bar_width = 30

    for score in range(10, 0, -1):
        count = dist.get(str(score), 0)
        filled = int(bar_width * count / max_count)
        bar = "█" * filled
        console.print(f"  [cyan]{score:2d}[/cyan]  {bar:<{bar_width}}  [dim]{count:,}[/dim]")


def print_stats(data: dict) -> None:
    lines: list[str] = []

    def add(label: str, key: str) -> None:
        val = data.get(key)
        if val is not None:
            lines.append(f"[bold]{label}:[/bold] {val:,}" if isinstance(val, int)
                         else f"[bold]{label}:[/bold] {val}")

    add("Watchers", "watchers")
    add("Plays", "plays")
    add("Collectors", "collectors")
    add("Collected episodes", "collected_episodes")
    add("Comments", "comments")
    add("Lists", "lists")
    add("Votes", "votes")
    add("Favorited", "favorited")

    console.print(Panel("\n".join(lines), title="[bold]Stats[/bold]", expand=False))


def print_aliases(aliases: list[dict]) -> None:
    if not aliases:
        console.print("[dim]No aliases found.[/dim]")
        return
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Country", width=8)
    table.add_column("Title")

    for a in sorted(aliases, key=lambda x: x.get("country", "")):
        table.add_row(
            (a.get("country") or "—").upper(),
            a.get("title", "—"),
        )
    console.print(table)


def print_watching(users: list[dict] | None) -> None:
    if not users:
        console.print("[dim]Nobody is watching right now.[/dim]")
        return
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Username")
    table.add_column("Name")
    table.add_column("VIP", width=4)

    for u in users:
        table.add_row(
            u.get("username", "—"),
            u.get("name") or "—",
            "✓" if u.get("vip") else "",
        )
    console.print(f"[dim]{len(users)} user(s) watching now[/dim]")
    console.print(table)


def _progress_bar(completed: int, total: int, width: int = 20) -> str:
    filled = int(width * completed / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def print_user_settings(data: dict) -> None:
    user = data.get("user", {})
    account = data.get("account", {})
    connections = data.get("connections", {})
    limits = data.get("limits", {})

    lines: list[str] = []

    def add(label: str, val: object) -> None:
        if val is not None and val != "" and val != []:
            lines.append(f"[bold]{label}:[/bold] {val}")

    add("Username", user.get("username"))
    add("Name", user.get("name"))
    if user.get("vip"):
        add("VIP", "yes")
    add("Location", user.get("location"))
    add("About", user.get("about"))
    joined = user.get("joined_at", "")
    add("Joined", joined[:10] if joined else None)
    add("Timezone", account.get("timezone"))
    add("Date format", account.get("date_format"))
    add("24hr time", account.get("time_24hr"))

    connected = [k for k, v in connections.items() if v]
    if connected:
        add("Connected", ", ".join(connected))

    wl = limits.get("watchlist", {}).get("item_count")
    if wl:
        add("Watchlist limit", wl)

    console.print(Panel("\n".join(lines), title="[bold]Account Settings[/bold]", expand=False))


def print_user_profile(data: dict) -> None:
    ids = data.get("ids", {})
    lines: list[str] = []

    def add(label: str, val: object) -> None:
        if val is not None and val != "" and val != []:
            lines.append(f"[bold]{label}:[/bold] {val}")

    add("Username", data.get("username"))
    add("Name", data.get("name"))
    if data.get("private"):
        add("Private", "yes")
    if data.get("vip"):
        add("VIP", "yes")
    joined = data.get("joined_at", "")
    add("Joined", joined[:10] if joined else None)
    add("Location", data.get("location"))
    add("About", data.get("about"))
    add("Slug", ids.get("slug"))

    console.print(Panel("\n".join(lines), title="[bold]User Profile[/bold]", expand=False))


def print_user_stats(data: dict, username: str = "") -> None:
    title = f"[bold]Stats — {username}[/bold]" if username else "[bold]Stats[/bold]"
    lines: list[str] = []

    def add(label: str, val: object) -> None:
        if val is not None:
            lines.append(
                f"[bold]{label}:[/bold] {val:,}" if isinstance(val, int)
                else f"[bold]{label}:[/bold] {val}"
            )

    movies = data.get("movies", {})
    episodes = data.get("episodes", {})
    shows = data.get("shows", {})
    network = data.get("network", {})

    if movies:
        lines.append("[cyan]Movies[/cyan]")
        add("  Watched", movies.get("watched"))
        add("  Plays", movies.get("plays"))
        add("  Minutes", movies.get("minutes"))
        add("  Collected", movies.get("collected"))
        add("  Ratings", movies.get("ratings"))

    if shows or episodes:
        lines.append("\n[cyan]Shows / Episodes[/cyan]")
        add("  Shows watched", shows.get("watched"))
        add("  Episodes watched", episodes.get("watched"))
        add("  Episode plays", episodes.get("plays"))
        add("  Episode minutes", episodes.get("minutes"))
        add("  Shows collected", shows.get("collected"))

    if network:
        lines.append("\n[cyan]Network[/cyan]")
        add("  Friends", network.get("friends"))
        add("  Followers", network.get("followers"))
        add("  Following", network.get("following"))

    console.print(Panel("\n".join(lines), title=title, expand=False))


def print_user_watching(data: dict | None) -> None:
    if not data:
        console.print("[dim]Not watching anything right now.[/dim]")
        return

    action = data.get("action", "")
    item_type = data.get("type", "")
    started_at = data.get("started_at", "")
    expires_at = data.get("expires_at", "")
    started_fmt = started_at[:16].replace("T", " ") if started_at else "—"
    expires_fmt = expires_at[:16].replace("T", " ") if expires_at else "—"

    if item_type == "movie":
        movie = data.get("movie", {})
        label = f"{movie.get('title', '—')} ({movie.get('year', '')})"
    elif item_type == "episode":
        ep = data.get("episode", {})
        show = data.get("show", {})
        s, e = ep.get("season", 0), ep.get("number", 0)
        ep_title = ep.get("title") or ""
        label = f"{show.get('title', '—')}  S{s:02d}E{e:02d}"
        if ep_title:
            label += f'  "{ep_title}"'
    else:
        label = "unknown"

    console.print(f"[green]Watching:[/green] {label}")
    console.print(f"[dim]Started: {started_fmt}  ·  Action: {action}  ·  Expires: {expires_fmt}[/dim]")


def print_user_network(items: list[dict], relation: str) -> None:
    if not items:
        console.print(f"[dim]No {relation}.[/dim]")
        return

    at_key = "friends_at" if relation == "friends" else "followed_at"
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Username")
    table.add_column("Name")
    table.add_column("VIP", width=4)
    table.add_column("Since", style="dim")

    for item in items:
        user = item.get("user", {})
        at = item.get(at_key, "")
        table.add_row(
            user.get("username", "—"),
            user.get("name") or "—",
            "✓" if user.get("vip") else "",
            at[:10] if at else "—",
        )

    console.print(f"[dim]{len(items)} {relation}[/dim]")
    console.print(table)


def print_public_lists(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]No lists found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("By", style="dim")
    table.add_column("Items", width=6, justify="right")
    table.add_column("Likes", width=6, justify="right")
    table.add_column("Comments", width=8, justify="right")
    table.add_column("Slug", style="dim")

    for row in results:
        lst = row.get("list", {})
        ids = lst.get("ids", {})
        table.add_row(
            lst.get("name", "—"),
            lst.get("user", {}).get("username", "—"),
            str(lst.get("item_count", "—")),
            str(row.get("like_count", 0)),
            str(row.get("comment_count", 0)),
            ids.get("slug", "—"),
        )

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_list_info(data: dict) -> None:
    name = data.get("name", "—")
    description = data.get("description") or ""
    privacy = data.get("privacy", "—")
    share_link = data.get("share_link", "")
    item_count = data.get("item_count", 0)
    likes = data.get("likes", 0)
    comment_count = data.get("comment_count", 0)
    sort_by = data.get("sort_by", "rank")
    sort_how = data.get("sort_how", "asc")
    ids = data.get("ids", {})
    user = data.get("user", {}).get("username", "—")

    lines = []
    if description:
        lines.append(description)
        lines.append("")
    lines.append(f"By:       {user}")
    lines.append(f"Privacy:  {privacy}")
    lines.append(f"Items:    {item_count}  Likes: {likes}  Comments: {comment_count}")
    lines.append(f"Sort:     {sort_by} {sort_how}")
    if share_link:
        lines.append(f"Link:     {share_link}")
    lines.append(f"[dim]trakt:{ids.get('trakt', '—')}  slug:{ids.get('slug', '—')}[/dim]")

    console.print(Panel("\n".join(lines), title=f"[bold]{name}[/bold]"))


def print_user_lists(items: list[dict]) -> None:
    if not items:
        console.print("[dim]No lists found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Privacy", width=8)
    table.add_column("Items", width=6, justify="right")
    table.add_column("Likes", width=6, justify="right")
    table.add_column("Slug", style="dim")

    for item in items:
        ids = item.get("ids", {})
        table.add_row(
            item.get("name", "—"),
            item.get("privacy", "—"),
            str(item.get("item_count", "—")),
            str(item.get("likes", "—")),
            ids.get("slug", "—"),
        )

    console.print(table)


def print_user_list_items(items: list[dict], meta: dict) -> None:
    if not items:
        console.print("[dim]List is empty.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Ep", style="dim", width=7)
    table.add_column("Notes", style="dim")

    for item in items:
        rank = str(item.get("rank", "—"))
        item_type = item.get("type", "")
        notes = item.get("notes") or ""
        if len(notes) > 40:
            notes = notes[:37] + "..."
        ep_str = ""

        if item_type == "movie":
            title = item.get("movie", {}).get("title", "—")
        elif item_type == "show":
            title = item.get("show", {}).get("title", "—")
        elif item_type == "season":
            obj = item.get("season", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{obj.get('number', 0):02d}"
        elif item_type == "episode":
            ep = item.get("episode", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{ep.get('season', 0):02d}E{ep.get('number', 0):02d}"
        elif item_type == "person":
            title = item.get("person", {}).get("name", "—")
        else:
            title = "—"

        table.add_row(rank, item_type, title, ep_str, notes)

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_user_hidden(items: list[dict], meta: dict) -> None:
    if not items:
        console.print("[dim]No hidden items.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Hidden", style="dim")
    table.add_column("Slug", style="dim")

    for item in items:
        item_type = item.get("type", "")
        hidden_at = item.get("hidden_at", "")
        hidden_fmt = hidden_at[:10] if hidden_at else "—"

        if item_type == "movie":
            obj = item.get("movie", {})
            title = obj.get("title", "—")
            slug = obj.get("ids", {}).get("slug", "—")
        elif item_type == "show":
            obj = item.get("show", {})
            title = obj.get("title", "—")
            slug = obj.get("ids", {}).get("slug", "—")
        elif item_type == "season":
            obj = item.get("season", {})
            show = item.get("show", {})
            title = f"{show.get('title', '—')}  S{obj.get('number', 0):02d}"
            slug = show.get("ids", {}).get("slug", "—")
        else:
            title = "—"
            slug = "—"

        table.add_row(item_type, title, hidden_fmt, slug)

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_person_info(person: dict) -> None:
    ids = person.get("ids", {})
    social = person.get("social_ids", {})
    name = person.get("name", "Unknown")
    lines: list[str] = []

    def add(label: str, val: object) -> None:
        if val is not None and val != "":
            lines.append(f"[bold]{label}:[/bold] {val}")

    add("Birthday", person.get("birthday"))
    add("Birthplace", person.get("birthplace"))
    if person.get("death"):
        add("Death", person.get("death"))
    add("Gender", person.get("gender"))
    add("Known for", person.get("known_for_department"))
    add("Homepage", person.get("homepage"))

    social_parts = [f"{k}: {v}" for k, v in social.items() if v]
    if social_parts:
        add("Social", "  ".join(social_parts))

    add("Trakt slug", ids.get("slug"))
    add("IMDB", ids.get("imdb"))
    add("TMDB", ids.get("tmdb"))

    bio = person.get("biography", "")
    if bio:
        lines.append("")
        lines.append(bio)

    console.print(Panel("\n".join(lines), title=f"[bold]{name}[/bold]", expand=False))


def print_person_credits(data: dict, media_type: str) -> None:
    """media_type: 'movies' or 'shows'"""
    item_key = "movie" if media_type == "movies" else "show"
    cast = data.get("cast", [])
    crew = data.get("crew", {})

    if cast:
        console.print("\n[bold cyan]Cast[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Characters")
        if media_type == "shows":
            table.add_column("Eps", justify="right", width=5)
        table.add_column("Title")
        table.add_column("Year", width=6, justify="right")
        table.add_column("Slug", style="dim")

        for credit in cast:
            chars = ", ".join(credit.get("characters") or []) or "—"
            item = credit.get(item_key, {})
            ids = item.get("ids", {})
            row = [chars]
            if media_type == "shows":
                ec = credit.get("episode_count")
                row.append(str(ec) if ec is not None else "—")
            row += [item.get("title", "—"), str(item.get("year") or "—"), ids.get("slug", "—")]
            table.add_row(*row)
        console.print(table)

    key_depts = ["directing", "writing", "created by", "production", "camera", "editing"]
    for dept in key_depts:
        members = crew.get(dept, [])
        if not members:
            continue
        console.print(f"\n[bold cyan]{dept.title()}[/bold cyan]")
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Jobs")
        table.add_column("Title")
        table.add_column("Year", width=6, justify="right")
        table.add_column("Slug", style="dim")

        for credit in members:
            jobs = ", ".join(credit.get("jobs") or []) or "—"
            item = credit.get(item_key, {})
            ids = item.get("ids", {})
            table.add_row(jobs, item.get("title", "—"),
                          str(item.get("year") or "—"), ids.get("slug", "—"))
        console.print(table)


def print_season_info(season: dict) -> None:
    number = season.get("number", "?")
    title = season.get("title") or f"Season {number}"
    rating = season.get("rating")
    votes = season.get("votes")
    episode_count = season.get("episode_count")
    aired = season.get("aired_episodes")
    first_aired = season.get("first_aired", "")
    network = season.get("network")
    overview = season.get("overview") or ""
    ids = season.get("ids", {})

    lines = []
    if first_aired:
        lines.append(f"First aired:  {first_aired[:10]}")
    if episode_count is not None:
        ep_str = f"Episodes:     {episode_count}"
        if aired is not None and aired != episode_count:
            ep_str += f" ({aired} aired)"
        lines.append(ep_str)
    if network:
        lines.append(f"Network:      {network}")
    if rating is not None:
        lines.append(f"Rating:       {rating:.1f}/10  ({votes} votes)")
    if overview:
        lines.append("")
        lines.append(overview)
    lines.append(f"[dim]trakt:{ids.get('trakt', '—')}  tmdb:{ids.get('tmdb', '—')}[/dim]")

    console.print(Panel("\n".join(lines), title=f"[bold]{title}[/bold]"))


def print_episode_info(ep: dict) -> None:
    ids = ep.get("ids", {})
    s = ep.get("season", "?")
    n = ep.get("number", "?")
    title = ep.get("title", "Unknown")

    lines: list[str] = []

    def add(label: str, val: object) -> None:
        if val is not None and val != "":
            lines.append(f"[bold]{label}:[/bold] {val}")

    ep_type = ep.get("episode_type", "")
    if ep_type:
        add("Type", ep_type.replace("_", " ").title())
    fa = ep.get("first_aired", "")
    add("First aired", fa[:16].replace("T", " ") + " UTC" if fa else None)
    add("Runtime", f"{ep['runtime']} min" if ep.get("runtime") else None)
    add("Rating", f"{ep['rating']:.1f}/10  ({ep['votes']:,} votes)"
        if ep.get("rating") is not None and ep.get("votes") is not None else None)
    add("Trakt ID", ids.get("trakt"))
    add("IMDB", ids.get("imdb"))
    add("TMDB", ids.get("tmdb"))
    add("TVDB", ids.get("tvdb"))

    overview = ep.get("overview", "")
    if overview:
        lines.append("")
        lines.append(overview)

    header = f"[bold]S{s:02d}E{n:02d}[/bold]  {title}"
    console.print(Panel("\n".join(lines), title=header, expand=False))


def print_show_progress(data: dict, mode: str) -> None:
    """mode is 'watched' or 'collection'."""
    aired = data.get("aired", 0)
    completed = data.get("completed", 0)
    pct = int(completed / aired * 100) if aired else 0

    if mode == "watched":
        ts = data.get("last_watched_at", "")
        ts_label = "Last watched"
        reset_at = data.get("reset_at")
    else:
        ts = data.get("last_collected_at", "")
        ts_label = "Last collected"
        reset_at = None

    ts_fmt = ts[:16].replace("T", " ") if ts else "—"
    bar = _progress_bar(completed, aired)

    console.print(f"\n[bold]{completed}[/bold]/{aired} episodes  [cyan]{bar}[/cyan]  {pct}%")
    console.print(f"[dim]{ts_label}: {ts_fmt}[/dim]")
    if reset_at:
        console.print(f"[dim]Re-watch started: {reset_at[:10]}[/dim]")
    console.print()

    seasons = data.get("seasons", [])
    if seasons:
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        table.add_column("Season", width=8)
        table.add_column("Done", width=8, justify="right")
        table.add_column("", width=22)

        for season in seasons:
            s_num = season.get("number", "?")
            s_aired = season.get("aired", 0)
            s_completed = season.get("completed", 0)
            s_pct = int(s_completed / s_aired * 100) if s_aired else 0
            s_bar = _progress_bar(s_completed, s_aired)
            label = f"Season {s_num}" if s_num != 0 else "Specials"
            table.add_row(label, f"{s_completed}/{s_aired}", f"[cyan]{s_bar}[/cyan]  {s_pct}%")

        console.print(table)

    next_ep = data.get("next_episode")
    last_ep = data.get("last_episode")

    if next_ep:
        s, e = next_ep.get("season", 0), next_ep.get("number", 0)
        title = next_ep.get("title") or "TBA"
        console.print(f"[bold]Next:[/bold]  [cyan]S{s:02d}E{e:02d}[/cyan]  \"{title}\"")
    else:
        verb = "watch" if mode == "watched" else "collect"
        console.print(f"[bold]Next:[/bold]  [dim]nothing left to {verb}[/dim]")

    if last_ep:
        s, e = last_ep.get("season", 0), last_ep.get("number", 0)
        title = last_ep.get("title") or ""
        console.print(f"[bold]Last:[/bold]  [cyan]S{s:02d}E{e:02d}[/cyan]  \"{title}\"")


def print_recommendations(results: list[dict], item_key: str) -> None:
    if not results:
        console.print("[dim]No recommendations found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title")
    table.add_column("Year", width=6, justify="right")
    table.add_column("Slug", style="dim")
    table.add_column("Favorited by", style="dim")

    for i, item in enumerate(results, 1):
        ids = item.get("ids", {})
        favorited_by = item.get("favorited_by", [])
        if favorited_by:
            fav_str = ", ".join(f["user"]["username"] for f in favorited_by if f.get("user"))
        else:
            fav_str = ""
        table.add_row(
            str(i),
            item.get("title", "—"),
            str(item.get("year") or "—"),
            ids.get("slug", "—"),
            fav_str,
        )

    console.print(table)


def print_checkin_result(data: dict) -> None:
    history_id = data.get("id")
    watched_at = data.get("watched_at", "")
    watched_fmt = watched_at[:16].replace("T", " ") + " UTC" if watched_at else "—"

    if "movie" in data:
        movie = data["movie"]
        title = movie.get("title", "—")
        year = movie.get("year", "")
        label = f"{title}" + (f" ({year})" if year else "")
    elif "episode" in data:
        ep = data["episode"]
        show = data.get("show", {})
        s, e = ep.get("season", 0), ep.get("number", 0)
        ep_title = ep.get("title") or ""
        label = f"{show.get('title', '—')}  S{s:02d}E{e:02d}"
        if ep_title:
            label += f'  "{ep_title}"'
    else:
        label = "unknown item"

    console.print(f"[green]Checked in:[/green] {label}")
    console.print(f"[dim]History ID: {history_id}  ·  at {watched_fmt}[/dim]")


def print_sync_last_activities(data: dict) -> None:
    def fmt(ts: str | None) -> str:
        return ts[:16].replace("T", " ") + " UTC" if ts else "—"

    console.print(f"[bold]Overall last activity:[/bold] {fmt(data.get('all'))}\n")

    groups = [
        ("Movies", data.get("movies", {})),
        ("Episodes", data.get("episodes", {})),
        ("Shows", data.get("shows", {})),
        ("Seasons", data.get("seasons", {})),
    ]
    for group_name, activities in groups:
        if not activities:
            continue
        console.print(f"[bold cyan]{group_name}[/bold cyan]")
        for key, ts in activities.items():
            label = key.replace("_at", "").replace("_", " ")
            console.print(f"  {label:<18} {fmt(ts)}")
        console.print()


def print_sync_watched(results: list[dict], type: str) -> None:
    if not results:
        console.print("[dim]Nothing watched yet.[/dim]")
        return

    item_key = "movie" if type == "movies" else "show"
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Plays", width=6, justify="right")
    table.add_column("Last Watched")
    table.add_column("Title")
    table.add_column("Slug", style="dim")

    for i, item in enumerate(results, 1):
        obj = item.get(item_key, {})
        ids = obj.get("ids", {})
        plays = str(item.get("plays", "—"))
        lw = item.get("last_watched_at", "")
        lw_fmt = lw[:16].replace("T", " ") if lw else "—"
        table.add_row(str(i), plays, lw_fmt, obj.get("title", "—"), ids.get("slug", "—"))

    console.print(table)


def print_sync_history(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]No history found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=10, justify="right")
    table.add_column("Watched At", width=16)
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Ep", style="dim", width=7)

    for item in results:
        watched_at = item.get("watched_at", "")
        watched_fmt = watched_at[:16].replace("T", " ") if watched_at else "—"
        item_type = item.get("type", "")
        history_id = str(item.get("id", "—"))

        if item_type == "movie":
            title = item.get("movie", {}).get("title", "—")
            ep_str = ""
        elif item_type == "episode":
            ep = item.get("episode", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{ep.get('season', 0):02d}E{ep.get('number', 0):02d}"
        else:
            title = "—"
            ep_str = ""

        table.add_row(history_id, watched_fmt, item_type, title, ep_str)

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_sync_ratings(results: list[dict]) -> None:
    if not results:
        console.print("[dim]No ratings found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Rating", width=7, justify="right")
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Ep", style="dim", width=7)
    table.add_column("Rated", style="dim")
    table.add_column("Slug", style="dim")

    for item in results:
        rating = item.get("rating", "—")
        item_type = item.get("type", "")
        rated_at = item.get("rated_at", "")
        rated_fmt = rated_at[:10] if rated_at else "—"
        ep_str = ""

        if item_type == "movie":
            obj = item.get("movie", {})
            title = obj.get("title", "—")
            ids = obj.get("ids", {})
        elif item_type == "show":
            obj = item.get("show", {})
            title = obj.get("title", "—")
            ids = obj.get("ids", {})
        elif item_type == "season":
            obj = item.get("season", {})
            show = item.get("show", {})
            title = show.get("title", "—")
            ids = show.get("ids", {})
            ep_str = f"S{obj.get('number', 0):02d}"
        elif item_type == "episode":
            ep = item.get("episode", {})
            show = item.get("show", {})
            title = show.get("title", "—")
            ids = show.get("ids", {})
            ep_str = f"S{ep.get('season', 0):02d}E{ep.get('number', 0):02d}"
        else:
            title = "—"
            ids = {}

        table.add_row(
            f"{rating}/10",
            item_type,
            title,
            ep_str,
            rated_fmt,
            ids.get("slug", "—"),
        )

    console.print(table)


def print_sync_watchlist(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]Watchlist is empty.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Rank", width=5, justify="right", style="dim")
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Ep", style="dim", width=7)
    table.add_column("Added", style="dim")
    table.add_column("Notes", style="dim")

    for item in results:
        rank = str(item.get("rank", "—"))
        item_type = item.get("type", "")
        listed_at = item.get("listed_at", "")
        listed_fmt = listed_at[:10] if listed_at else "—"
        notes = item.get("notes") or ""
        if len(notes) > 40:
            notes = notes[:37] + "..."
        ep_str = ""

        if item_type == "movie":
            title = item.get("movie", {}).get("title", "—")
        elif item_type == "show":
            title = item.get("show", {}).get("title", "—")
        elif item_type == "season":
            obj = item.get("season", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{obj.get('number', 0):02d}"
        elif item_type == "episode":
            ep = item.get("episode", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{ep.get('season', 0):02d}E{ep.get('number', 0):02d}"
        else:
            title = "—"

        table.add_row(rank, item_type, title, ep_str, listed_fmt, notes)

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_sync_collection(results: list[dict], type: str) -> None:
    if not results:
        console.print("[dim]Collection is empty.[/dim]")
        return

    if type == "movies":
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Collected")
        table.add_column("Title")
        table.add_column("Year", width=6, justify="right")
        table.add_column("Slug", style="dim")

        for i, item in enumerate(results, 1):
            movie = item.get("movie", {})
            ids = movie.get("ids", {})
            ca = item.get("collected_at", "")
            table.add_row(
                str(i),
                ca[:10] if ca else "—",
                movie.get("title", "—"),
                str(movie.get("year") or "—"),
                ids.get("slug", "—"),
            )
    else:
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Last Collected")
        table.add_column("Title")
        table.add_column("Seasons", width=8, justify="right")
        table.add_column("Episodes", width=9, justify="right")
        table.add_column("Slug", style="dim")

        for i, item in enumerate(results, 1):
            show = item.get("show", {})
            ids = show.get("ids", {})
            lc = item.get("last_collected_at", "")
            seasons = item.get("seasons", [])
            ep_count = sum(len(s.get("episodes", [])) for s in seasons)
            table.add_row(
                str(i),
                lc[:10] if lc else "—",
                show.get("title", "—"),
                str(len(seasons)),
                str(ep_count),
                ids.get("slug", "—"),
            )

    console.print(table)


def print_sync_playback(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]No paused playback found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=8, justify="right")
    table.add_column("Progress", width=9, justify="right")
    table.add_column("Type", width=8)
    table.add_column("Title")
    table.add_column("Ep", style="dim", width=7)
    table.add_column("Paused At", style="dim")

    for item in results:
        pb_id = str(item.get("id", "—"))
        progress = item.get("progress", 0)
        item_type = item.get("type", "")
        paused_at = item.get("paused_at", "")
        paused_fmt = paused_at[:16].replace("T", " ") if paused_at else "—"
        ep_str = ""

        if item_type == "movie":
            title = item.get("movie", {}).get("title", "—")
        elif item_type == "episode":
            ep = item.get("episode", {})
            title = item.get("show", {}).get("title", "—")
            ep_str = f"S{ep.get('season', 0):02d}E{ep.get('number', 0):02d}"
        else:
            title = "—"

        table.add_row(pb_id, f"{progress:.1f}%", item_type, title, ep_str, paused_fmt)

    console.print(table)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_sync_result(data: dict) -> None:
    added = data.get("added", {})
    updated = data.get("updated", {})
    deleted = data.get("deleted", {})
    existing = data.get("existing", {})
    not_found = data.get("not_found", {})

    for label, d, color in [
        ("Added", added, "green"),
        ("Updated", updated, "green"),
        ("Deleted", deleted, "green"),
        ("Existing", existing, "dim"),
    ]:
        if d and any(isinstance(v, int) and v > 0 for v in d.values()):
            counts = ", ".join(f"{v} {k}" for k, v in d.items() if isinstance(v, int) and v > 0)
            console.print(f"[{color}]{label}:[/{color}] {counts}")

    nf_items = {k: v for k, v in not_found.items() if isinstance(v, list) and v}
    if nf_items:
        nf_str = ", ".join(f"{len(v)} {k}" for k, v in nf_items.items())
        console.print(f"[yellow]Not found:[/yellow] {nf_str}")


def print_comment(data: dict) -> None:
    """Print a single comment as a panel."""
    user = data.get("user", {}).get("username", "unknown")
    comment_id = data.get("id", "—")
    comment_text = data.get("comment", "")
    spoiler = data.get("spoiler", False)
    review = data.get("review", False)
    likes = data.get("likes", 0)
    reply_count = data.get("replies", 0)
    created_at = data.get("created_at", "")
    created_fmt = created_at[:16].replace("T", " ") if created_at else "—"

    tags = []
    if spoiler:
        tags.append("[yellow]SPOILER[/yellow]")
    if review:
        tags.append("[blue]REVIEW[/blue]")

    meta_parts = [f"#{comment_id}", f"by {user}", created_fmt, f"♥ {likes}", f"replies: {reply_count}"]
    if tags:
        meta_parts.extend(tags)
    subtitle = "[dim]" + "  ".join(meta_parts) + "[/dim]"

    console.print(Panel(comment_text, subtitle=subtitle))


def print_comments(results: list[dict], meta: dict) -> None:
    if not results:
        console.print("[dim]No comments found.[/dim]")
        return
    for item in results:
        print_comment(item)
    footer = _pagination_footer(meta)
    if footer:
        console.print(f"[dim]{footer}[/dim]")


def print_episode_summary(ep: dict | None, label: str) -> None:
    if ep is None:
        console.print(f"[dim]No {label} episode found.[/dim]")
        return
    s = ep.get("season", "?")
    n = ep.get("number", "?")
    title = ep.get("title") or "TBA"
    ids = ep.get("ids", {})
    console.print(
        f"[bold]{label.title()}:[/bold]  "
        f"[cyan]S{s:02d}E{n:02d}[/cyan]  \"{title}\"  "
        f"[dim](trakt:{ids.get('trakt', '—')})[/dim]"
    )
