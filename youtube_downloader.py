"""
Module de recherche YouTube et de téléchargement en MP3.

Utilise yt-dlp pour rechercher la meilleure correspondance sur YouTube
et télécharger l'audio en MP3.
"""

import os
import re
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import yt_dlp

# Répertoire du script pour localiser ffmpeg embarqué
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FFMPEG_DIR = os.path.join(_SCRIPT_DIR, "ffmpeg")


def _sanitize_filename(name: str) -> str:
    """Remplace les caractères interdits dans un nom de fichier."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)


class YoutubeDownloader:
    """Recherche et télécharge des pistes audio depuis YouTube en MP3."""

    def __init__(self, output_dir: str, max_workers: int = 6) -> None:
        """
        Initialise le téléchargeur.

        Args:
            output_dir: Répertoire de destination des fichiers MP3.
            max_workers: Nombre de téléchargements simultanés.
        """
        self._output_dir = output_dir
        self._max_workers = max_workers
        os.makedirs(output_dir, exist_ok=True)

    def _build_ydl_opts(self, output_template: str) -> dict:
        return {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "concurrent_fragment_downloads": 4,
            "ffmpeg_location": _FFMPEG_DIR,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

    def download_track(self, title: str, artist: str) -> str | None:
        """
        Recherche la piste sur YouTube et la télécharge en MP3.

        Args:
            title:  Titre de la chanson.
            artist: Nom de l'artiste.

        Returns:
            Chemin absolu du fichier MP3 créé, ou None en cas d'échec.
        """
        safe_name = _sanitize_filename(f"{artist} - {title}")
        mp3_path = os.path.join(self._output_dir, f"{safe_name}.mp3")

        # Skip si déjà téléchargé
        if os.path.exists(mp3_path):
            return mp3_path

        query = f"ytsearch1:{artist} - {title}"
        output_template = os.path.join(self._output_dir, f"{safe_name}.%(ext)s")

        opts = self._build_ydl_opts(output_template)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([query])
            return mp3_path if os.path.exists(mp3_path) else None
        except yt_dlp.utils.DownloadError as exc:
            print(f"  [ERREUR] Impossible de télécharger « {artist} - {title} » : {exc}")
            return None

    def download_tracks(self, tracks: list[dict]) -> list[str]:
        """
        Télécharge une liste de pistes en parallèle.

        Args:
            tracks: Liste de dictionnaires avec les clés 'title' et 'artist'.

        Returns:
            Liste des chemins MP3 téléchargés avec succès.
        """
        downloaded: list[str] = []
        total = len(tracks)
        cancelled = False

        print(f"\n⚡ Téléchargement en parallèle ({self._max_workers} simultanés)…\n")

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {}
            for idx, track in enumerate(tracks, start=1):
                title = track["title"]
                artist = track["artist"]
                future = executor.submit(self.download_track, title, artist)
                futures[future] = (idx, artist, title)

            try:
                for future in as_completed(futures):
                    idx, artist, title = futures[future]
                    try:
                        path = future.result()
                    except Exception:
                        path = None
                    if path:
                        print(f"  [{idx}/{total}] ✓ {artist} - {title}")
                        downloaded.append(path)
                    else:
                        print(f"  [{idx}/{total}] ✗ {artist} - {title}")
            except KeyboardInterrupt:
                print("\n\n⚠ Interruption ! Annulation des téléchargements en cours…")
                cancelled = True
                executor.shutdown(wait=False, cancel_futures=True)

        if cancelled:
            print(f"  {len(downloaded)} piste(s) téléchargée(s) avant l'interruption.")

        return downloaded
