"""
Module de récupération et d'exportation des playlists Spotify en CSV.

Utilise l'API Spotify via la bibliothèque spotipy avec le flux Client Credentials.
Les variables SPOTIPY_CLIENT_ID et SPOTIPY_CLIENT_SECRET doivent être définies
dans un fichier .env ou dans les variables d'environnement.
"""

import csv
import os
import re

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()


def _extract_playlist_id(url: str) -> str:
    """Extrait l'identifiant de la playlist depuis une URL Spotify."""
    # Formats acceptés :
    #   https://open.spotify.com/playlist/<id>?si=...
    #   spotify:playlist:<id>
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"Impossible d'extraire l'ID de playlist depuis : {url}")
    return match.group(1)


class SpotifyExporter:
    """Récupère les pistes d'une playlist Spotify et les exporte en CSV."""

    def __init__(self) -> None:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise EnvironmentError(
                "Les variables d'environnement SPOTIPY_CLIENT_ID et "
                "SPOTIPY_CLIENT_SECRET doivent être définies."
            )

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
        self._sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_tracks(self, playlist_url: str) -> list[dict]:
        """
        Retourne la liste des pistes d'une playlist Spotify.

        Chaque piste est un dictionnaire avec les clés :
            - title   : titre de la chanson
            - artist  : artiste principal
            - album   : titre de l'album
            - duration: durée en secondes
        """
        playlist_id = _extract_playlist_id(playlist_url)
        tracks: list[dict] = []

        results = self._sp.playlist_items(
            playlist_id,
            fields="items(track(name,artists,album(name),duration_ms)),next",
            additional_types=["track"],
        )

        while results:
            for item in results["items"]:
                track = item.get("track")
                if not track:
                    continue
                artists = ", ".join(a["name"] for a in track.get("artists", []))
                tracks.append(
                    {
                        "title": track["name"],
                        "artist": artists,
                        "album": track["album"]["name"],
                        "duration": round(track["duration_ms"] / 1000),
                    }
                )
            results = self._sp.next(results) if results.get("next") else None

        return tracks

    def export_to_csv(self, tracks: list[dict], csv_path: str) -> str:
        """
        Enregistre la liste de pistes dans un fichier CSV.

        Retourne le chemin absolu du fichier créé.
        """
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
