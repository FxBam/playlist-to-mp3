"""
playlist-to-mp3 — Convertisseur de playlist Spotify en fichiers MP3.

Usage :
    python main.py <spotify_playlist_url> [options]
    python main.py --from-csv playlist.csv

Exemples :
    python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    python main.py --from-csv playlist.csv
    python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --csv-only
"""

import argparse
import csv
import os
import sys

from spotify_exporter import SpotifyExporter
from youtube_downloader import YoutubeDownloader


def default_output_dir() -> str:
    """Retourne le répertoire 'playlist convertie' dans le dossier Téléchargements."""
    home = os.path.expanduser("~")
    # Essaie les noms courants du dossier Téléchargements selon le système
    for downloads_name in ("Downloads", "Téléchargements", "Descargas", "Transferências"):
        candidate = os.path.join(home, downloads_name)
        if os.path.isdir(candidate):
            return os.path.join(candidate, "playlist convertie")
    # Repli sur ~/Downloads/playlist convertie
    return os.path.join(home, "Downloads", "playlist convertie")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="playlist-to-mp3",
        description="Convertit une playlist Spotify en fichiers MP3.",
    )
    parser.add_argument(
        "playlist_url",
        nargs="?",
        default=None,
        help="URL de la playlist Spotify (ex : https://open.spotify.com/playlist/…)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="DOSSIER",
        help=(
            "Dossier de destination des MP3 "
            "(défaut : ~/Downloads/playlist convertie)"
        ),
    )
    parser.add_argument(
        "--csv",
        "-c",
        default=None,
        metavar="FICHIER_CSV",
        help=(
            "Chemin du fichier CSV exporté "
            "(défaut : <DOSSIER>/playlist.csv)"
        ),
    )
    parser.add_argument(
        "--csv-only",
        action="store_true",
        help="Exporte uniquement le CSV sans télécharger les MP3.",
    )
    parser.add_argument(
        "--from-csv",
        default=None,
        metavar="FICHIER_CSV",
        help="Charger les pistes depuis un CSV existant (saute l'étape Spotify).",
    )
    args = parser.parse_args(argv)

    if not args.from_csv and not args.playlist_url:
        args.playlist_url = input("🎵 Entrez le lien de la playlist Spotify (ou chemin CSV) : ").strip()
        if not args.playlist_url:
            print("Erreur : aucun lien fourni.")
            sys.exit(1)
        # Si l'utilisateur entre un fichier CSV directement
        if args.playlist_url.endswith(".csv") and os.path.isfile(args.playlist_url):
            args.from_csv = args.playlist_url
            args.playlist_url = None

    return args


def load_tracks_from_csv(csv_path: str) -> list[dict]:
    """Charge les pistes depuis un fichier CSV existant."""
    tracks = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Supporte les colonnes : title/artist ou Track Name/Artist Name
            title = row.get("title") or row.get("Track Name") or row.get("Song Name") or ""
            artist = row.get("artist") or row.get("Artist Name") or row.get("Artist Name(s)") or ""
            album = row.get("album") or row.get("Album Name") or ""
            duration = row.get("duration") or row.get("Duration (ms)") or "0"
            if title.strip():
                tracks.append({
                    "title": title.strip(),
                    "artist": artist.strip(),
                    "album": album.strip(),
                    "duration": duration,
                })
    return tracks


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    output_dir = args.output or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    csv_path = args.csv or os.path.join(output_dir, "playlist.csv")

    print("=" * 60)
    print("  playlist-to-mp3")
    print("=" * 60)

    if args.from_csv:
        # ── Mode CSV : charger depuis un fichier existant ──────────
        print(f"  CSV       : {args.from_csv}")
        print(f"  Dossier   : {output_dir}")
        print("=" * 60)

        print("\n[1/2] Chargement des pistes depuis le CSV…")
        try:
            tracks = load_tracks_from_csv(args.from_csv)
        except Exception as exc:
            print(f"\n[ERREUR] Lecture du CSV impossible : {exc}")
            return 1

        if not tracks:
            print("[AVERTISSEMENT] Aucune piste trouvée dans le CSV.")
            return 0

        print(f"  → {len(tracks)} piste(s) chargée(s).")

        print("\n[2/2] Téléchargement des MP3 depuis YouTube…")
        downloader = YoutubeDownloader(output_dir)
        downloaded = downloader.download_tracks(tracks)

    else:
        # ── Mode Spotify : récupérer puis télécharger ──────────────
        print(f"  Playlist  : {args.playlist_url}")
        print(f"  Dossier   : {output_dir}")
        print(f"  CSV       : {csv_path}")
        print("=" * 60)

        # Étape 1 : Récupération de la playlist Spotify
        print("\n[1/3] Récupération des pistes depuis Spotify…")
        try:
            exporter = SpotifyExporter(args.playlist_url)
            tracks = exporter.get_tracks()
        except Exception as exc:
            print(f"\n[ERREUR] Récupération de la playlist impossible : {exc}")
            return 1

        if not tracks:
            print("[AVERTISSEMENT] Aucune piste trouvée dans la playlist.")
            return 0

        print(f"  → {len(tracks)} piste(s) trouvée(s).")

        # Étape 2 : Export CSV
        print("\n[2/3] Export de la playlist en CSV…")
        try:
            saved_csv = exporter.export_to_csv(tracks, csv_path)
            print(f"  → CSV enregistré : {saved_csv}")
        except Exception as exc:
            print(f"\n[ERREUR] Export CSV impossible : {exc}")
            return 1

        if args.csv_only:
            print("\nMode --csv-only activé. Téléchargement MP3 ignoré.")
            return 0

        # Étape 3 : Téléchargement MP3
        print("\n[3/3] Téléchargement des MP3 depuis YouTube…")
        downloader = YoutubeDownloader(output_dir)
        downloaded = downloader.download_tracks(tracks)

    print("\n" + "=" * 60)
    print(f"  Terminé ! {len(downloaded)}/{len(tracks)} piste(s) téléchargée(s).")
    print(f"  Dossier : {output_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
