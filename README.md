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
git clone https://github.com/louis/linvoc.git
cd linvoc

# Créer un environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer linvoc en mode éditable
pip install -e .
```

> [!NOTE]
> Bien que Python soit un langage interprété, `pip` génère automatiquement un script "wrapper" (un binaire de lancement) nommé `linvoc` dans le dossier `.venv/bin/`. C'est ce fichier que nous utiliserons pour lancer l'application.

### 3. Téléchargement du modèle vocal (Vosk)

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

Depuis le dossier du projet, avec l'environnement virtuel activé :

```bash
linvoc                # Lancement standard
linvoc --lang en      # Si vous avez un modèle anglais
linvoc --check        # Vérification des dépendances
```

> [!TIP]
> Si l'environnement n'est pas activé, vous pouvez toujours lancer :
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
Vous devez pointer directement vers le lanceur dans votre environnement virtuel :
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
