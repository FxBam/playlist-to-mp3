# 🎵 playlist-to-mp3

Convertit une playlist Spotify en fichiers MP3 téléchargés depuis YouTube.

## Fonctionnalités

- Récupère automatiquement toutes les pistes d'une playlist Spotify
- Exporte les métadonnées (titre, artiste, album, durée) dans un fichier CSV
- Recherche chaque chanson sur YouTube
- Télécharge en MP3 haute qualité (320 kbps)
- Sauvegarde dans le dossier `playlist convertie` du répertoire Téléchargements

## Prérequis

- **Python 3.10+**
- **FFmpeg** installé et accessible dans le PATH ([télécharger ici](https://ffmpeg.org/download.html))
- Un compte développeur Spotify avec des **identifiants API** (Client ID + Client Secret)

### Obtenir les identifiants Spotify

1. Aller sur [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Créer une application
3. Récupérer le **Client ID** et le **Client Secret**

## Installation

```bash
git clone https://github.com/FxBam/playlist-to-mp3.git
cd playlist-to-mp3
pip install -r requirements.txt
```

## Configuration

Définir les variables d'environnement Spotify :

### Windows (PowerShell)

```powershell
$env:SPOTIPY_CLIENT_ID = "votre_client_id"
$env:SPOTIPY_CLIENT_SECRET = "votre_client_secret"
```

### Linux / macOS

```bash
export SPOTIPY_CLIENT_ID="votre_client_id"
export SPOTIPY_CLIENT_SECRET="votre_client_secret"
```

Ou créer un fichier `.env` à la racine du projet :

```
SPOTIPY_CLIENT_ID=votre_client_id
SPOTIPY_CLIENT_SECRET=votre_client_secret
```

## Utilisation

```bash
python playlist_to_mp3.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
```

Le programme va :

1. Récupérer les pistes de la playlist via l'API Spotify
2. Créer un dossier `playlist convertie` dans vos Téléchargements
3. Exporter un fichier CSV avec les métadonnées
4. Télécharger chaque chanson en MP3 320 kbps depuis YouTube

## Structure du projet

```
playlist-to-mp3/
├── playlist_to_mp3.py   # Script principal
├── requirements.txt     # Dépendances Python
├── .gitignore
└── README.md
```

## Dépendances

| Paquet   | Rôle                                        |
|----------|---------------------------------------------|
| spotipy  | Accès à l'API Spotify                       |
| yt-dlp   | Recherche YouTube et téléchargement audio   |
| FFmpeg   | Conversion audio en MP3 (outil externe)     |

## Licence

Ce projet est libre d'utilisation.