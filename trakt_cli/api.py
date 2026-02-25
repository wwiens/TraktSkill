from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.trakt.tv"


class TraktClient:
    def __init__(self, api_key: str, access_token: str | None = None) -> None:
        self._headers = {
            "Content-Type": "application/json",
            "trakt-api-key": api_key,
            "trakt-api-version": "2",
        }
        if access_token:
            self._headers["Authorization"] = f"Bearer {access_token}"

    @property
    def is_authenticated(self) -> bool:
        return "Authorization" in self._headers

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        page: int | None = 1,
        limit: int | None = 10,
    ) -> tuple[Any, dict[str, int | None]]:
        all_params: dict[str, Any] = {}
        if page is not None:
            all_params["page"] = page
        if limit is not None:
            all_params["limit"] = limit
        if params:
            all_params.update(params)

        with httpx.Client(headers=self._headers) as client:
            response = client.get(f"{BASE_URL}{path}", params=all_params)
            response.raise_for_status()

        pagination = {
            "page": _int_header(response, "X-Pagination-Page"),
            "limit": _int_header(response, "X-Pagination-Limit"),
            "page_count": _int_header(response, "X-Pagination-Page-Count"),
            "item_count": _int_header(response, "X-Pagination-Item-Count"),
        }
        return response.json(), pagination

    def lookup(
        self,
        id_type: str,
        id_value: str,
        type_filter: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], dict]:
        params = {}
        if type_filter:
            params["type"] = type_filter
        return self._get(f"/search/{id_type}/{id_value}", params=params, page=page, limit=limit)

    def search_shows(
        self, query: str, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get("/search/show", params={"query": query}, page=page, limit=limit)

    def get_show(self, show_id: str) -> tuple[dict, dict]:
        body, meta = self._get(f"/shows/{show_id}", params={"extended": "full"})
        return body, meta

    def trending_shows(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/shows/trending", page=page, limit=limit)

    def popular_shows(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/shows/popular", page=page, limit=limit)

    def favorited_shows(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/favorited/{period}", page=page, limit=limit)

    def played_shows(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/played/{period}", page=page, limit=limit)

    def watched_shows(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/watched/{period}", page=page, limit=limit)

    def collected_shows(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/collected/{period}", page=page, limit=limit)

    def anticipated_shows(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/shows/anticipated", page=page, limit=limit)

    def updated_shows(
        self, start_date: str, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/updates/{start_date}", page=page, limit=limit)

    # --- Movies ---

    def search_movies(
        self, query: str, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get("/search/movie", params={"query": query}, page=page, limit=limit)

    def get_movie(self, movie_id: str) -> tuple[dict, dict]:
        body, meta = self._get(f"/movies/{movie_id}", params={"extended": "full"})
        return body, meta

    def trending_movies(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/movies/trending", page=page, limit=limit)

    def popular_movies(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/movies/popular", page=page, limit=limit)

    def favorited_movies(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/favorited/{period}", page=page, limit=limit)

    def played_movies(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/played/{period}", page=page, limit=limit)

    def watched_movies(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/watched/{period}", page=page, limit=limit)

    def collected_movies(
        self, period: str = "weekly", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/collected/{period}", page=page, limit=limit)

    def anticipated_movies(self, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get("/movies/anticipated", page=page, limit=limit)

    def boxoffice_movies(self) -> tuple[list[dict], dict]:
        return self._get("/movies/boxoffice", page=1, limit=10)

    def updated_movies(
        self, start_date: str, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/updates/{start_date}", page=page, limit=limit)

    # --- Calendars ---

    def _get_nullable(self, path: str) -> Any | None:
        """GET a resource that may return 204 or 404 (no content / not found)."""
        with httpx.Client(headers=self._headers) as client:
            response = client.get(f"{BASE_URL}{path}")
            if response.status_code in (204, 404):
                return None
            response.raise_for_status()
            return response.json()

    def _post(self, path: str, body: dict) -> Any:
        with httpx.Client(headers=self._headers) as client:
            response = client.post(f"{BASE_URL}{path}", json=body)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()

    def _put(self, path: str, body: dict) -> Any:
        with httpx.Client(headers=self._headers) as client:
            response = client.put(f"{BASE_URL}{path}", json=body)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()

    def _delete_req(self, path: str) -> None:
        with httpx.Client(headers=self._headers) as client:
            response = client.delete(f"{BASE_URL}{path}")
            response.raise_for_status()

    # --- Show sub-resources ---

    def show_seasons(self, show_id: str) -> list[dict]:
        body, _ = self._get(f"/shows/{show_id}/seasons", params={"extended": "full"},
                            page=None, limit=None)
        return body

    def show_episodes(self, show_id: str, season: int) -> list[dict]:
        body, _ = self._get(f"/shows/{show_id}/seasons/{season}", page=None, limit=None)
        return body

    def show_people(self, show_id: str) -> dict:
        body, _ = self._get(f"/shows/{show_id}/people", page=None, limit=None)
        return body

    def show_related(self, show_id: str, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get(f"/shows/{show_id}/related", page=page, limit=limit)

    def show_ratings(self, show_id: str) -> dict:
        body, _ = self._get(f"/shows/{show_id}/ratings", page=None, limit=None)
        return body

    def show_stats(self, show_id: str) -> dict:
        body, _ = self._get(f"/shows/{show_id}/stats", page=None, limit=None)
        return body

    def show_aliases(self, show_id: str) -> list[dict]:
        body, _ = self._get(f"/shows/{show_id}/aliases", page=None, limit=None)
        return body

    def show_watching(self, show_id: str) -> list[dict] | None:
        return self._get_nullable(f"/shows/{show_id}/watching")

    def show_next_episode(self, show_id: str) -> dict | None:
        return self._get_nullable(f"/shows/{show_id}/next_episode")

    def show_last_episode(self, show_id: str) -> dict | None:
        return self._get_nullable(f"/shows/{show_id}/last_episode")

    # --- People ---

    def person_info(self, person_id: str) -> dict:
        body, _ = self._get(f"/people/{person_id}", params={"extended": "full"},
                            page=None, limit=None)
        return body

    def person_movies(self, person_id: str) -> dict:
        body, _ = self._get(f"/people/{person_id}/movies", page=None, limit=None)
        return body

    def person_shows(self, person_id: str) -> dict:
        body, _ = self._get(f"/people/{person_id}/shows", page=None, limit=None)
        return body

    # --- Season sub-resources ---

    def season_info(self, show_id: str, season: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/info",
            params={"extended": "full"},
            page=None,
            limit=None,
        )
        return body

    def season_people(self, show_id: str, season: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/people", page=None, limit=None
        )
        return body

    def season_ratings(self, show_id: str, season: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/ratings", page=None, limit=None
        )
        return body

    def season_stats(self, show_id: str, season: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/stats", page=None, limit=None
        )
        return body

    def season_watching(self, show_id: str, season: int) -> list[dict] | None:
        return self._get_nullable(f"/shows/{show_id}/seasons/{season}/watching")

    def season_comments(
        self,
        show_id: str,
        season: int,
        sort: str = "newest",
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], dict]:
        return self._get(
            f"/shows/{show_id}/seasons/{season}/comments/{sort}", page=page, limit=limit
        )

    # --- Episode sub-resources ---

    def episode_info(self, show_id: str, season: int, episode: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}",
            params={"extended": "full"},
            page=None,
            limit=None,
        )
        return body

    def episode_people(self, show_id: str, season: int, episode: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}/people",
            page=None,
            limit=None,
        )
        return body

    def episode_ratings(self, show_id: str, season: int, episode: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}/ratings",
            page=None,
            limit=None,
        )
        return body

    def episode_stats(self, show_id: str, season: int, episode: int) -> dict:
        body, _ = self._get(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}/stats",
            page=None,
            limit=None,
        )
        return body

    def episode_watching(self, show_id: str, season: int, episode: int) -> list[dict] | None:
        return self._get_nullable(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}/watching"
        )

    def show_comments(
        self, show_id: str, sort: str = "newest", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/shows/{show_id}/comments/{sort}", page=page, limit=limit)

    def episode_comments(
        self,
        show_id: str,
        season: int,
        episode: int,
        sort: str = "newest",
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], dict]:
        return self._get(
            f"/shows/{show_id}/seasons/{season}/episodes/{episode}/comments/{sort}",
            page=page,
            limit=limit,
        )

    def show_watched_progress(
        self,
        show_id: str,
        hidden: bool = False,
        specials: bool = False,
    ) -> dict:
        params: dict = {}
        if hidden:
            params["hidden"] = "true"
        if specials:
            params["specials"] = "true"
        body, _ = self._get(
            f"/shows/{show_id}/progress/watched", params=params, page=None, limit=None
        )
        return body

    def show_collection_progress(
        self,
        show_id: str,
        hidden: bool = False,
        specials: bool = False,
    ) -> dict:
        params: dict = {}
        if hidden:
            params["hidden"] = "true"
        if specials:
            params["specials"] = "true"
        body, _ = self._get(
            f"/shows/{show_id}/progress/collection", params=params, page=None, limit=None
        )
        return body

    # --- Movie sub-resources ---

    def movie_people(self, movie_id: str) -> dict:
        body, _ = self._get(f"/movies/{movie_id}/people", page=None, limit=None)
        return body

    def movie_related(self, movie_id: str, page: int = 1, limit: int = 10) -> tuple[list[dict], dict]:
        return self._get(f"/movies/{movie_id}/related", page=page, limit=limit)

    def movie_ratings(self, movie_id: str) -> dict:
        body, _ = self._get(f"/movies/{movie_id}/ratings", page=None, limit=None)
        return body

    def movie_stats(self, movie_id: str) -> dict:
        body, _ = self._get(f"/movies/{movie_id}/stats", page=None, limit=None)
        return body

    def movie_aliases(self, movie_id: str) -> list[dict]:
        body, _ = self._get(f"/movies/{movie_id}/aliases", page=None, limit=None)
        return body

    def movie_watching(self, movie_id: str) -> list[dict] | None:
        return self._get_nullable(f"/movies/{movie_id}/watching")

    # --- Public Lists ---

    def lists_trending(
        self, list_type: str = "personal", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/lists/trending/{list_type}", page=page, limit=limit)

    def lists_popular(
        self, list_type: str = "personal", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/lists/popular/{list_type}", page=page, limit=limit)

    def list_get(self, list_id: int) -> dict:
        body, _ = self._get(f"/lists/{list_id}", page=None, limit=None)
        return body

    def list_items(
        self,
        list_id: int,
        item_type: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], dict]:
        path = f"/lists/{list_id}/items"
        if item_type:
            path += f"/{item_type}"
        return self._get(path, page=page, limit=limit)

    def list_like(self, list_id: int) -> None:
        self._post(f"/lists/{list_id}/like", {})

    def list_unlike(self, list_id: int) -> None:
        self._delete_req(f"/lists/{list_id}/like")

    def movie_comments(
        self, movie_id: str, sort: str = "newest", page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/movies/{movie_id}/comments/{sort}", page=page, limit=limit)

    # --- Users ---

    def user_settings(self) -> dict:
        body, _ = self._get("/users/settings", page=None, limit=None)
        return body

    def user_profile(self, user_id: str) -> dict:
        body, _ = self._get(f"/users/{user_id}", page=None, limit=None)
        return body

    def user_stats(self, user_id: str) -> dict:
        body, _ = self._get(f"/users/{user_id}/stats", page=None, limit=None)
        return body

    def user_watching(self, user_id: str) -> dict | None:
        return self._get_nullable(f"/users/{user_id}/watching")

    def user_followers(self, user_id: str) -> list[dict]:
        body, _ = self._get(f"/users/{user_id}/followers", page=None, limit=None)
        return body

    def user_following(self, user_id: str) -> list[dict]:
        body, _ = self._get(f"/users/{user_id}/following", page=None, limit=None)
        return body

    def user_friends(self, user_id: str) -> list[dict]:
        body, _ = self._get(f"/users/{user_id}/friends", page=None, limit=None)
        return body

    def user_history(
        self,
        user_id: str,
        type: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[dict], dict]:
        path = f"/users/{user_id}/history"
        if type:
            path += f"/{type}"
        return self._get(path, page=page, limit=limit)

    def user_ratings(
        self, user_id: str, type: str = "all", rating: int | None = None
    ) -> list[dict]:
        path = f"/users/{user_id}/ratings/{type}"
        if rating is not None:
            path += f"/{rating}"
        body, _ = self._get(path, page=None, limit=None)
        return body

    def user_watched(self, user_id: str, type: str) -> list[dict]:
        body, _ = self._get(f"/users/{user_id}/watched/{type}", page=None, limit=None)
        return body

    def user_lists(self, user_id: str) -> list[dict]:
        body, _ = self._get(f"/users/{user_id}/lists", page=None, limit=None)
        return body

    def user_list_items(
        self, user_id: str, list_id: str, page: int = 1, limit: int = 20
    ) -> tuple[list[dict], dict]:
        return self._get(f"/users/{user_id}/lists/{list_id}/items", page=page, limit=limit)

    def user_hidden(
        self, section: str, page: int = 1, limit: int = 20
    ) -> tuple[list[dict], dict]:
        return self._get(f"/users/hidden/{section}", page=page, limit=limit)

    def user_hide(self, section: str, body: dict) -> dict:
        return self._post(f"/users/hidden/{section}", body)

    def user_unhide(self, section: str, body: dict) -> dict:
        return self._post(f"/users/hidden/{section}/remove", body)

    def user_follow(self, user_id: str) -> dict:
        return self._post(f"/users/{user_id}/follow", {})

    def user_unfollow(self, user_id: str) -> None:
        self._delete_req(f"/users/{user_id}/follow")

    # --- Recommendations ---

    def recommendations_movies(
        self,
        limit: int = 10,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> tuple[list[dict], dict]:
        params: dict = {}
        if ignore_collected:
            params["ignore_collected"] = "true"
        if ignore_watchlisted:
            params["ignore_watchlisted"] = "true"
        return self._get("/recommendations/movies", params=params, page=None, limit=limit)

    def recommendations_shows(
        self,
        limit: int = 10,
        ignore_collected: bool = False,
        ignore_watchlisted: bool = False,
    ) -> tuple[list[dict], dict]:
        params: dict = {}
        if ignore_collected:
            params["ignore_collected"] = "true"
        if ignore_watchlisted:
            params["ignore_watchlisted"] = "true"
        return self._get("/recommendations/shows", params=params, page=None, limit=limit)

    def recommendations_hide_movie(self, id: str) -> None:
        self._delete_req(f"/recommendations/movies/{id}")

    def recommendations_hide_show(self, id: str) -> None:
        self._delete_req(f"/recommendations/shows/{id}")

    # --- Checkin ---

    def checkin(self, body: dict) -> dict:
        """POST /checkin. Raises HTTPStatusError on failure, including 409 (already checked in)."""
        return self._post("/checkin", body)

    def checkin_delete(self) -> None:
        """DELETE /checkin — remove any active checkin."""
        self._delete_req("/checkin")

    # --- Comments ---

    def comment_get(self, comment_id: int) -> dict:
        body, _ = self._get(f"/comments/{comment_id}", page=None, limit=None)
        return body

    def comment_post(self, body: dict) -> dict:
        return self._post("/comments", body)

    def comment_update(self, comment_id: int, text: str, spoiler: bool = False) -> dict:
        return self._put(f"/comments/{comment_id}", {"comment": text, "spoiler": spoiler})

    def comment_delete(self, comment_id: int) -> None:
        self._delete_req(f"/comments/{comment_id}")

    def comment_replies(
        self, comment_id: int, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        return self._get(f"/comments/{comment_id}/replies", page=page, limit=limit)

    def comment_reply(self, comment_id: int, text: str, spoiler: bool = False) -> dict:
        return self._post(f"/comments/{comment_id}/replies", {"comment": text, "spoiler": spoiler})

    def comment_like(self, comment_id: int) -> None:
        self._post(f"/comments/{comment_id}/like", {})

    def comment_unlike(self, comment_id: int) -> None:
        self._delete_req(f"/comments/{comment_id}/like")

    # --- Sync ---

    def sync_last_activities(self) -> dict:
        body, _ = self._get("/sync/last_activities", page=None, limit=None)
        return body

    def sync_playback(
        self, type: str | None = None, page: int = 1, limit: int = 10
    ) -> tuple[list[dict], dict]:
        path = f"/sync/playback/{type}" if type else "/sync/playback"
        return self._get(path, page=page, limit=limit)

    def sync_remove_playback(self, id: int) -> None:
        self._delete_req(f"/sync/playback/{id}")

    def sync_watched(self, type: str) -> list[dict]:
        body, _ = self._get(f"/sync/watched/{type}", page=None, limit=None)
        return body

    def sync_history(
        self,
        type: str | None = None,
        id: int | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[dict], dict]:
        path = "/sync/history"
        if type:
            path += f"/{type}"
            if id is not None:
                path += f"/{id}"
        return self._get(path, page=page, limit=limit)

    def sync_ratings(self, type: str = "all", rating: int | None = None) -> list[dict]:
        path = f"/sync/ratings/{type}"
        if rating is not None:
            path += f"/{rating}"
        body, _ = self._get(path, page=None, limit=None)
        return body

    def sync_watchlist(
        self,
        type: str = "all",
        sort_by: str = "rank",
        sort_how: str = "asc",
        page: int | None = None,
        limit: int | None = None,
    ) -> tuple[list[dict], dict]:
        return self._get(
            f"/sync/watchlist/{type}/{sort_by}/{sort_how}",
            page=page,
            limit=limit,
        )

    def sync_collection(self, type: str) -> list[dict]:
        body, _ = self._get(f"/sync/collection/{type}", page=None, limit=None)
        return body

    def sync_add_history(self, body: dict) -> dict:
        return self._post("/sync/history", body)

    def sync_remove_history(self, body: dict) -> dict:
        return self._post("/sync/history/remove", body)

    def sync_add_ratings(self, body: dict) -> dict:
        return self._post("/sync/ratings", body)

    def sync_remove_ratings(self, body: dict) -> dict:
        return self._post("/sync/ratings/remove", body)

    def sync_add_watchlist(self, body: dict) -> dict:
        return self._post("/sync/watchlist", body)

    def sync_remove_watchlist(self, body: dict) -> dict:
        return self._post("/sync/watchlist/remove", body)

    def _calendar(self, path: str) -> list[dict]:
        body, _ = self._get(path, page=None, limit=None)
        return body

    def calendar_shows(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/shows/{start_date}/{days}")

    def calendar_new_shows(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/shows/new/{start_date}/{days}")

    def calendar_premieres(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/shows/premieres/{start_date}/{days}")

    def calendar_finales(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/shows/finales/{start_date}/{days}")

    def calendar_movies(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/movies/{start_date}/{days}")

    def calendar_streaming(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/streaming/{start_date}/{days}")

    def calendar_dvd(self, start_date: str, days: int) -> list[dict]:
        base = "my" if self.is_authenticated else "all"
        return self._calendar(f"/calendars/{base}/dvd/{start_date}/{days}")


def _int_header(response: httpx.Response, name: str) -> int | None:
    val = response.headers.get(name)
    return int(val) if val is not None else None


def refresh_token(refresh_token_val: str, client_id: str, client_secret: str) -> dict:
    """POST /oauth/token with grant_type=refresh_token.
    Returns new token dict on 200, raises httpx.HTTPStatusError on 401 (invalid/expired)."""
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/oauth/token",
            json={
                "refresh_token": refresh_token_val,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()


def device_code(client_id: str) -> dict:
    """POST /oauth/device/code — returns device_code, user_code, verification_url, expires_in, interval."""
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/oauth/device/code",
            json={"client_id": client_id},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()


def device_token(code: str, client_id: str, client_secret: str) -> dict | None:
    """POST /oauth/device/token — returns token dict on 200, None on 400 (pending).
    Raises httpx.HTTPStatusError for terminal states (410 expired, 418 denied, etc.)."""
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/oauth/device/token",
            json={"code": code, "client_id": client_id, "client_secret": client_secret},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 400:
            return None
        response.raise_for_status()
        return response.json()
