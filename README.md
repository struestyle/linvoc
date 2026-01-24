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

### 1. Prérequis système

Selon votre environnement, certains outils sont nécessaires pour l'injection de texte :

- **X11** : `xdotool`
- **Wayland** : `ydotool` (recommandé) ou `wl-clipboard`

```bash
# Debian / Ubuntu / Mint
sudo apt install xdotool ydotool wl-clipboard

# Fedora
sudo dnf install xdotool ydotool wl-clipboard

# Arch Linux
sudo pacman -S xdotool ydotool wl-clipboard
```

> [!IMPORTANT]
> Pour **ydotool**, assurez-vous que le service est actif et que votre utilisateur a les droits :
> ```bash
> sudo systemctl enable --now ydotool
> sudo usermod -aG ydotool $USER
> # Redémarrez votre session après l'ajout au groupe.
> ```

### 2. Installation de linvoc

```bash
# Cloner le dépôt
git clone https://github.com/louis/linvoc.git
cd linvoc

# Installer en mode éditable (recommandé pour le développement)
pip install -e .
```

### 3. Configuration de la voix (Vosk)

linvoc nécessite [nerd-dictation](https://github.com/ideasman42/nerd-dictation) pour fonctionner.

```bash
# Installation de nerd-dictation
pip install "git+https://github.com/ideasman42/nerd-dictation.git#subdirectory=package/python"

# Téléchargement du modèle français (via l'outil intégré)
nerd-dictation setup-vosk fr
```

## 🚀 Utilisation

### Lancement

Une fois installé, vous pouvez lancer linvoc directement depuis votre terminal :

```bash
linvoc                # Lance l'interface par défaut
linvoc --lang en      # Utilise le modèle anglais
linvoc --check        # Vérifie que tout est correctement installé
linvoc --info         # Affiche les détails de votre environnement
```

### Fonctionnement

1. **Positionnez** votre curseur dans un champ texte.
2. **Lancez** linvoc (via terminal ou raccourci clavier).
3. **Appuyez sur Espace** ou cliquez sur le micro pour démarrer la dictée.
4. **Parlez** ! Le micro devient rouge pour indiquer l'écoute.
5. **Appuyez sur Espace** à nouveau pour arrêter : le texte est automatiquement injecté.

### Raccourcis clavier (dans la fenêtre)

| Touche | Action |
|--------|--------|
| `Espace` | Démarrer / Arrêter la dictée |
| `Échap` | Annuler et fermer l'application |

## ⚙️ Configuration du raccourci global

Pour une expérience optimale, créez un raccourci clavier système (ex: `Super+H`).

### KDE Plasma
**Paramètres** → **Raccourcis** → **Commandes** : ajouter `linvoc`.

### GNOME
**Paramètres** → **Clavier** → **Raccourcis personnalisés** : ajouter une commande `linvoc`.

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
