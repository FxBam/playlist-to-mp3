#!/usr/bin/env python3
"""
playlist-to-mp3 : Convertit une playlist Spotify en fichiers MP3
téléchargés depuis YouTube.

Usage :
    python playlist_to_mp3.py <lien_playlist_spotify>
"""

import argparse
import csv
import os
import re
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp


def get_downloads_folder():
    """Retourne le chemin du dossier Téléchargements de l'utilisateur."""
    if sys.platform == "win32":
        import winreg
        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            downloads = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        return downloads
    return os.path.join(os.path.expanduser("~"), "Downloads")


def extract_playlist_id(url):
    """Extrait l'identifiant de la playlist depuis l'URL Spotify."""
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    if not match:
        print("Erreur : URL de playlist Spotify invalide.")
        sys.exit(1)
    return match.group(1)


def fetch_playlist_tracks(playlist_url):
    """Récupère les pistes d'une playlist Spotify via l'API."""
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    playlist_id = extract_playlist_id(playlist_url)

    try:
        playlist = sp.playlist(playlist_id)
    except spotipy.exceptions.SpotifyException as exc:
        print(f"Erreur Spotify : {exc}")
        sys.exit(1)

    playlist_name = playlist["name"]
    tracks = []
    results = playlist["tracks"]

    while True:
        for item in results["items"]:
            track = item.get("track")
            if track is None:
                continue
            title = track["name"]
            artists = ", ".join(a["name"] for a in track["artists"])
            album = track["album"]["name"]
            duration_ms = track["duration_ms"]
            duration_s = duration_ms // 1000
            duration_str = f"{duration_s // 60}:{duration_s % 60:02d}"
            tracks.append({
                "title": title,
                "artists": artists,
                "album": album,
                "duration": duration_str,
            })
        if results["next"]:
            results = sp.next(results)
        else:
            break

    print(f"Playlist « {playlist_name} » — {len(tracks)} piste(s) trouvée(s).")
    return playlist_name, tracks


def export_csv(tracks, csv_path):
    """Exporte la liste de pistes dans un fichier CSV."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "artists", "album", "duration"])
        writer.writeheader()
        writer.writerows(tracks)
    print(f"CSV exporté : {csv_path}")


def download_track(query, output_dir, index, total):
    """Recherche la chanson sur YouTube et la télécharge en MP3 HD."""
    print(f"\n[{index}/{total}] Recherche : {query}")

    ydl_opts = {
        "format": "bestaudio/best",
        "default_search": "ytsearch1",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        print(f"  ✓ Téléchargé avec succès")
    except Exception as exc:
        print(f"  ✗ Échec du téléchargement : {exc}")


def main():
    parser = argparse.ArgumentParser(
        description="Convertit une playlist Spotify en fichiers MP3 via YouTube."
    )
    parser.add_argument("playlist_url", help="Lien de la playlist Spotify")
    args = parser.parse_args()

    # 1. Récupérer les pistes depuis Spotify
    playlist_name, tracks = fetch_playlist_tracks(args.playlist_url)

    if not tracks:
        print("Aucune piste trouvée dans la playlist.")
        sys.exit(0)

    # 2. Créer le dossier de sortie
    downloads = get_downloads_folder()
    output_dir = os.path.join(downloads, "playlist convertie")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Dossier de sortie : {output_dir}")

    # 3. Exporter le CSV
    csv_path = os.path.join(output_dir, f"{playlist_name}.csv")
    export_csv(tracks, csv_path)

    # 4. Télécharger chaque piste en MP3 HD depuis YouTube
    total = len(tracks)
    for i, track in enumerate(tracks, start=1):
        query = f"{track['artists']} - {track['title']}"
        download_track(query, output_dir, i, total)

    print(f"\n{'='*50}")
    print(f"Terminé ! {total} piste(s) traitée(s).")
    print(f"Fichiers dans : {output_dir}")


if __name__ == "__main__":
    main()
