# 🎵 playlist-to-mp3

Convertissez n'importe quelle playlist Spotify en fichiers **MP3** (192 kbps) stockés dans votre dossier Téléchargements, en une seule commande.

---

## ✨ Fonctionnalités

- 📋 Récupération automatique des pistes depuis l’API Spotify
- 📄 Export de la playlist au format **CSV**
- 🔍 Recherche automatique de chaque chanson sur **YouTube**
- ⬇️ Téléchargement et conversion en **MP3 192 kbps** via `yt-dlp` + FFmpeg
- ⚡ **Téléchargement parallèle** (6 pistes simultanées par défaut)
- 🔁 **Skip automatique** des fichiers déjà téléchargés
- 📂 Import depuis un **fichier CSV existant** (mode `--from-csv`)
- ⏹️ **Interruption propre** avec Ctrl+C (conserve les fichiers déjà téléchargés)
- 📁 Sauvegarde dans `~/Downloads/playlist convertie`

---

## 🛠️ Prérequis

| Outil    | Version minimale | Installation                          |
|----------|-----------------|---------------------------------------|
| Python   | 3.11            | [python.org](https://python.org)      |

> **FFmpeg** est inclus dans le dossier `ffmpeg/` du projet. Aucune installation supplémentaire n’est nécessaire.

---

## 🚀 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/FxBam/playlist-to-mp3.git
cd playlist-to-mp3

# 2. Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# 3. Installer les dépendances Python
pip install -r requirements.txt
```

---

## 🔑 Configuration de l'API Spotify

1. Connectez-vous sur [Spotify for Developers](https://developer.spotify.com/dashboard)
2. Créez une application (**Create App**)
3. Notez votre **Client ID** et votre **Client Secret**
4. Créez un fichier `.env` à la racine du projet :

```env
SPOTIPY_CLIENT_ID=votre_client_id_ici
SPOTIPY_CLIENT_SECRET=votre_client_secret_ici
```

> ⚠️ Le fichier `.env` est exclu du dépôt Git (`.gitignore`). Ne le partagez jamais.

---

## 📖 Utilisation

### Conversion complète (CSV + MP3)

```bash
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
```

### Avec dossier de destination personnalisé

```bash
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --output ~/Musique/MaPlaylist
```

### Export CSV uniquement (sans télécharger les MP3)

```bash
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" --csv-only
```

### Toutes les options

```
usage: playlist-to-mp3 [-h] [--output DOSSIER] [--csv FICHIER_CSV] [--csv-only] [--from-csv FICHIER_CSV] [playlist_url]

Convertit une playlist Spotify en fichiers MP3.

arguments positionnels :
  playlist_url          URL de la playlist Spotify

options :
  -h, --help            Affiche ce message d’aide
  -o, --output DOSSIER  Dossier de destination (défaut : ~/Downloads/playlist convertie)
  -c, --csv FICHIER_CSV Chemin du fichier CSV (défaut : <DOSSIER>/playlist.csv)
  --csv-only            Exporte uniquement le CSV, sans télécharger les MP3
  --from-csv FICHIER_CSV  Charger les pistes depuis un CSV existant (saute l’étape Spotify)
```

### Depuis un fichier CSV existant

```bash
python main.py --from-csv playlist.csv
```

Le programme accepte aussi de coller directement un chemin CSV quand il demande le lien de la playlist.

---

## 📂 Structure du projet

```
playlist-to-mp3/
├── main.py               # Point d'entrée CLI
├── spotify_exporter.py   # Récupération playlist Spotify + export CSV
├── youtube_downloader.py # Recherche YouTube + téléchargement MP3 parallèle
├── ffmpeg/               # Binaires FFmpeg embarqués (ffmpeg.exe, ffprobe.exe)
├── requirements.txt      # Dépendances Python
├── .env                  # Clés API Spotify (à créer, non versionné)
└── README.md             # Ce fichier
```

---

## 📄 Format du CSV exporté

| title         | artist        | album             | duration |
|---------------|---------------|-------------------|----------|
| Blinding Lights | The Weeknd  | After Hours       | 200      |
| Shape of You  | Ed Sheeran    | ÷ (Divide)        | 234      |

Le champ `duration` est en secondes.

---

## ⚠️ Avertissements

- Le téléchargement de contenu protégé par le droit d'auteur est soumis aux lois de votre pays et aux conditions d'utilisation de YouTube. Utilisez cet outil uniquement pour un usage personnel et légal.
- Certaines pistes peuvent ne pas être trouvées sur YouTube si leur titre diffère entre les deux plateformes.
- FFmpeg est inclus dans le dossier `ffmpeg/` du projet et utilisé automatiquement.

---

## 📝 Licence

Ce projet est fourni à titre éducatif. L'auteur décline toute responsabilité quant à l'utilisation qui en est faite.