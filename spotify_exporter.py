"""
Module de récupération et d'exportation des playlists Spotify en CSV.

Utilise un token anonyme extrait de la page embed Spotify —
aucune clé API ni compte développeur requis.
"""

import csv
import os
import re
import time

import requests

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _extract_playlist_id(url: str) -> str:
    """Extrait l'identifiant de la playlist depuis une URL Spotify."""
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"Impossible d'extraire l'ID de playlist depuis : {url}")
    return match.group(1)


def _get_anonymous_token(playlist_id: str) -> str:
    """Obtient un token Spotify anonyme via la page embed (pas de clé API)."""
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})

    # Méthode 1 : page embed
    try:
        embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
        resp = session.get(embed_url, timeout=15)
        resp.raise_for_status()
        match = re.search(r'"accessToken":"([^"]+)"', resp.text)
        if match:
            return match.group(1)
    except requests.RequestException:
        pass

    # Méthode 2 : endpoint get_access_token avec cookies de session
    try:
        session.get("https://open.spotify.com/", timeout=10)
        resp = session.get(
            "https://open.spotify.com/get_access_token?reason=transport&productType=web_player",
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json().get("accessToken")
        if token:
            return token
    except requests.RequestException:
        pass

    raise RuntimeError(
        "Impossible d'obtenir un token Spotify anonyme. "
        "Utilisez --from-csv avec un CSV exporté depuis https://www.chosic.com/spotify-playlist-exporter/"
    )


class SpotifyExporter:
    """Récupère les pistes d'une playlist Spotify et les exporte en CSV."""

    API_BASE = "https://api.spotify.com/v1"

    def __init__(self, playlist_url: str) -> None:
        self._playlist_id = _extract_playlist_id(playlist_url)
        self._token = _get_anonymous_token(self._playlist_id)
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": _USER_AGENT,
        }

    def get_tracks(self) -> list[dict]:
        """
        Retourne la liste des pistes d'une playlist Spotify.

        Chaque piste est un dictionnaire avec les clés :
            - title   : titre de la chanson
            - artist  : artiste(s)
            - album   : titre de l'album
            - duration: durée en secondes
        """
        playlist_id = self._playlist_id
        tracks: list[dict] = []
        url = f"{self.API_BASE}/playlists/{playlist_id}/tracks"
        params = {"limit": 100, "offset": 0}

        while url:
            for attempt in range(5):
                resp = requests.get(url, headers=self._headers, params=params, timeout=15)
                if resp.status_code == 429:
                    raw_wait = resp.headers.get("Retry-After", str(2 ** attempt))
                    wait = min(int(raw_wait), 30)
                    print(f"  ⏳ Rate limit Spotify, attente {wait}s…")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            else:
                raise RuntimeError("Trop de tentatives (429) sur l'API Spotify.")

            data = resp.json()

            for item in data.get("items", []):
                track = item.get("track")
                if not track or not track.get("name"):
                    continue
                artists = ", ".join(a["name"] for a in track.get("artists", []))
                tracks.append({
                    "title": track["name"],
                    "artist": artists,
                    "album": track["album"]["name"],
                    "duration": round(track["duration_ms"] / 1000),
                })

            url = data.get("next")
            params = {}  # next URL contient déjà les paramètres

        return tracks

    def export_to_csv(self, tracks: list[dict], csv_path: str) -> str:
        """Enregistre la liste de pistes dans un fichier CSV."""
        parent = os.path.dirname(os.path.abspath(csv_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["title", "artist", "album", "duration"]
            )
            writer.writeheader()
            writer.writerows(tracks)
        return os.path.abspath(csv_path)
