"""
Module de récupération et d'exportation des playlists Spotify en CSV.

Utilise un token anonyme Spotify — aucune clé API ni compte développeur requis.
"""

import csv
import os
import re

import requests


def _extract_playlist_id(url: str) -> str:
    """Extrait l'identifiant de la playlist depuis une URL Spotify."""
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"Impossible d'extraire l'ID de playlist depuis : {url}")
    return match.group(1)


def _get_anonymous_token() -> str:
    """Obtient un token d'accès Spotify anonyme (pas besoin de clés API)."""
    resp = requests.get(
        "https://open.spotify.com/get_access_token?reason=transport&productType=web_player",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json().get("accessToken")
    if not token:
        raise RuntimeError("Impossible d'obtenir un token Spotify anonyme.")
    return token


class SpotifyExporter:
    """Récupère les pistes d'une playlist Spotify et les exporte en CSV."""

    API_BASE = "https://api.spotify.com/v1"

    def __init__(self) -> None:
        self._token = _get_anonymous_token()
        self._headers = {"Authorization": f"Bearer {self._token}"}

    def get_tracks(self, playlist_url: str) -> list[dict]:
        """
        Retourne la liste des pistes d'une playlist Spotify.

        Chaque piste est un dictionnaire avec les clés :
            - title   : titre de la chanson
            - artist  : artiste(s)
            - album   : titre de l'album
            - duration: durée en secondes
        """
        playlist_id = _extract_playlist_id(playlist_url)
        tracks: list[dict] = []
        url = f"{self.API_BASE}/playlists/{playlist_id}/tracks"
        params = {"limit": 100, "offset": 0}

        while url:
            resp = requests.get(url, headers=self._headers, params=params, timeout=15)
            resp.raise_for_status()
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
