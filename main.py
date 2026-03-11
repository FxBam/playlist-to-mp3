"""
playlist-to-mp3 — Convertisseur de playlist Spotify en fichiers MP3.

Usage :
    python main.py <spotify_playlist_url> [options]

Exemples :
    python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --output ~/Musique/MaPlaylist
    python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --csv-only
"""

import argparse
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    output_dir = args.output or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    csv_path = args.csv or os.path.join(output_dir, "playlist.csv")

    print("=" * 60)
    print("  playlist-to-mp3")
    print("=" * 60)
    print(f"  Playlist  : {args.playlist_url}")
    print(f"  Dossier   : {output_dir}")
    print(f"  CSV       : {csv_path}")
    print("=" * 60)

    # ── Étape 1 : Récupération de la playlist Spotify ──────────────
    print("\n[1/3] Connexion à l'API Spotify et récupération des pistes…")
    try:
        exporter = SpotifyExporter()
    except EnvironmentError as exc:
        print(f"\n[ERREUR] {exc}")
        print(
            "\nConseils :\n"
            "  1. Créez un fichier .env à la racine du projet avec :\n"
            "       SPOTIPY_CLIENT_ID=<votre_client_id>\n"
            "       SPOTIPY_CLIENT_SECRET=<votre_client_secret>\n"
            "  2. Ou exportez ces variables dans votre terminal.\n"
            "  Voir README.md pour les instructions détaillées."
        )
        return 1

    try:
        tracks = exporter.get_tracks(args.playlist_url)
    except Exception as exc:
        print(f"\n[ERREUR] Récupération de la playlist impossible : {exc}")
        return 1

    if not tracks:
        print("[AVERTISSEMENT] Aucune piste trouvée dans la playlist.")
        return 0

    print(f"  → {len(tracks)} piste(s) trouvée(s).")

    # ── Étape 2 : Export CSV ───────────────────────────────────────
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

    # ── Étape 3 : Téléchargement MP3 ──────────────────────────────
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
