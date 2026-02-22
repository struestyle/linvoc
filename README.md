# 🎤 linvoc - Dictée vocale pour Linux

Application de dictée vocale similaire à Windows (Win+H) pour Linux, compatible X11 et Wayland.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## ✨ Fonctionnalités

- 🎙️ **Dictée vocale offline** via [nerd-dictation](https://github.com/ideasman42/nerd-dictation) + Vosk.
- 🖥️ **Compatible X11 et Wayland** (détection automatique).
- 🎨 **Interface minimaliste** flottante et thémable.
- ⌨️ **Injection automatique** du texte dans l'application active.
- 🔐 **Vie privée respectée** : Aucun transfert de données vocales vers le cloud.
- 🌐 **Support multi-langues** (français, anglais, etc.).

## 📦 Installation

L'installation se déroule en trois étapes : les outils système pour l'interaction avec votre bureau, l'environnement Python, et enfin le modèle de reconnaissance vocale.

### 1. Dépendances système

`linvoc` n'est pas une simple application Python isolée ; elle doit interagir avec votre serveur graphique (X11 ou Wayland) pour simuler des pressions de touches (injection de texte). Pour cela, des outils système natifs sont indispensables.

```bash
# Debian / Ubuntu / Mint
sudo apt install xdotool ydotool wl-clipboard

# Fedora
sudo dnf install xdotool ydotool wl-clipboard

# Arch Linux
sudo pacman -S xdotool ydotool wl-clipboard
```

> [!IMPORTANT]
> **Pour les utilisateurs de Wayland (GNOME, KDE récent) :**
> `ydotool` nécessite un démon en arrière-plan. Activez-le ainsi :
> ```bash
> sudo systemctl enable --now ydotool
> sudo usermod -aG ydotool $USER
> # Redémarrez votre session pour appliquer les changements de groupe.
> ```

### 2. Installation de linvoc

Sur les distributions Linux modernes, Python protège son système (norme PEP 668). Vous **devez** utiliser un environnement virtuel pour installer des paquets proprement.

```bash
# Cloner le dépôt et entrer dedans
git clone https://github.com/struestyle/linvoc.git
cd linvoc

# Créer un environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer linvoc en mode éditable
pip install -e .
```

> [!NOTE]
> Cette commande installe automatiquement toutes les dépendances nécessaires, y compris `nerd-dictation`, `vosk` et `PySide6`. `pip` génère également un script "wrapper" nommé `linvoc` dans le dossier `.venv/bin/`.

### 3. Installation rapide (recommandé)

Le script `install.sh` automatise les étapes 2 ci-dessus et installe la commande `linvoc` dans `~/.local/bin/` pour qu'elle soit accessible depuis n'importe où :

```bash
git clone https://github.com/struestyle/linvoc.git
cd linvoc
./install.sh
```

Le script effectue automatiquement :
- Création du venv et installation des dépendances
- Installation d'un wrapper `linvoc` dans `~/.local/bin/`
- Vérification que `~/.local/bin` est dans le `PATH`

> [!NOTE]
> Si `~/.local/bin` n'est pas dans votre `PATH`, le script vous indiquera la ligne à ajouter dans votre `~/.bashrc` ou `~/.zshrc`.

### 4. Téléchargement du modèle vocal (Vosk)

`nerd-dictation` nécessite un modèle Vosk pour fonctionner hors-ligne.

```bash
# Créer le dossier de configuration
mkdir -p ~/.config/nerd-dictation
cd ~/.config/nerd-dictation

# Télécharger et extraire le modèle français
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
mv vosk-model-small-fr-0.22 model
rm vosk-model-small-fr-0.22.zip
```

## 🚀 Utilisation

### Lancement direct

Depuis n'importe quel terminal (après installation via `install.sh`) :

```bash
linvoc                # Lancement standard
linvoc --lang en      # Si vous avez un modèle anglais
linvoc --check        # Vérification des dépendances
```

> [!TIP]
> Si vous n'avez pas utilisé `install.sh`, vous pouvez lancer depuis le dossier du projet :
> `./.venv/bin/linvoc` ou `python3 -m src.main`

### Fonctionnement

1. **Positionnez** votre curseur dans un champ texte.
2. **Lancez** linvoc (via terminal ou raccourci clavier).
3. **Appuyez sur Espace** pour démarrer.
4. **Parlez** (le micro devient rouge).
5. **Appuyez sur Espace** à nouveau : le texte est injecté.

## ⌨️ Raccourci Clavier Global (Le plus pratique)

Pour utiliser `linvoc` comme un vrai outil système (similaire à Win+H), créez un raccourci clavier global dans vos paramètres système (ex: `Super+H`).

### Commande à utiliser :

Si vous avez installé via `install.sh`, utilisez simplement :
```bash
linvoc --start
```

Sinon, pointez directement vers le lanceur dans votre environnement virtuel :
```bash
/chemin/complet/vers/linvoc/.venv/bin/linvoc --start
```

> [!TIP]
> L'argument `--start` permet de lancer l'application et de commencer l'écoute immédiatement, ce qui rend l'expérience beaucoup plus fluide.

### Configuration selon votre bureau :

- **KDE Plasma** : Paramètres → Raccourcis → Commandes → Ajouter.
- **GNOME** : Paramètres → Clavier → Raccourcis personnalisés → Ajouter (+).
- **XFCE** : Paramètres → Clavier → Raccourcis d'applications → Ajouter.

## 🔧 Dépannage

- **"Le texte ne s'insère pas"** : Vérifiez que `xdotool` (X11) ou `ydotool` (Wayland) est installé.
- **"nerd-dictation non trouvé"** : Réinstallez nerd-dictation via la commande pip fournie plus haut.
- **Latence** : La transcription locale peut prendre 1 à 2 secondes après la fin de la parole selon votre processeur.

## 🛠️ Développement & Packaging

Ce projet utilise `pyproject.toml` pour sa gestion.

```bash
# Pour créer un package distribuable (.whl)
pip install build
python3 -m build
```

## 🌍 Langues supportées

Vous pouvez installer n'importe quel modèle supporté par Vosk :
`nerd-dictation setup-vosk <code_langue>` (fr, en, de, es, it, ru, zh, etc.)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
