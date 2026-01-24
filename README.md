# 🎤 linvoc - Dictée vocale pour Linux

Application de dictée vocale similaire à Windows (Win+H) pour Linux, compatible X11 et Wayland.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## ✨ Fonctionnalités

- 🎙️ Dictée vocale offline via [nerd-dictation](https://github.com/ideasman42/nerd-dictation) + Vosk
- 🖥️ Compatible X11 et Wayland
- 🎨 Interface minimaliste flottante (80x80px)
- ⌨️ Injection automatique du texte dans l'application active
- 🌐 Support multi-langues (français, anglais, etc.)

## 📦 Installation

### Prérequis

1. **nerd-dictation** et un modèle vocal Vosk :

```bash
# Installer depuis GitHub (avec le sous-répertoire correct)
pip install "git+https://github.com/ideasman42/nerd-dictation.git#subdirectory=package/python"

# Télécharger le modèle français (~50 MB)
mkdir -p ~/.config/nerd-dictation
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
mv vosk-model-small-fr-0.22 ~/.config/nerd-dictation/model
rm vosk-model-small-fr-0.22.zip
```

2. **Outil d'injection de texte** selon votre session :

**X11 :**
```bash
# Debian/Ubuntu
sudo apt install xdotool

# Fedora
sudo dnf install xdotool

# Arch
sudo pacman -S xdotool
```

**Wayland :**
```bash
# Debian/Ubuntu
sudo apt install wl-clipboard ydotool

# Démarrer le daemon ydotool
sudo systemctl enable --now ydotool
sudo usermod -aG ydotool $USER
# Déconnectez-vous puis reconnectez-vous
```

### Installation de linvoc

```bash
# Cloner le dépôt
git clone https://github.com/louis/linvoc.git
cd linvoc

# Installer les dépendances
pip install -r requirements.txt

# Installer linvoc
pip install -e .
```

## 🚀 Utilisation

### Lancement

```bash
# Lancer l'application
linvoc

# Afficher les infos d'environnement
linvoc --info

# Vérifier les dépendances
linvoc --check

# Utiliser l'anglais
linvoc --lang en
```

### Fonctionnement

1. **Positionnez** votre curseur dans un champ texte
2. **Lancez** linvoc (fenêtre flottante apparaît)
3. **Cliquez** sur la fenêtre ou appuyez sur **Espace** pour démarrer
4. **Parlez** (le micro devient rouge)
5. **Cliquez** à nouveau pour arrêter → le texte est injecté

### Raccourcis clavier

| Touche | Action |
|--------|--------|
| `Espace` | Démarrer/Arrêter la dictée |
| `Échap` | Annuler et fermer |

## ⚙️ Configuration du raccourci global

linvoc n'intercepte pas les raccourcis système. Configurez-le manuellement :

### KDE Plasma (Le plus simple)

1. **Paramètres** → **Raccourcis** → **Commandes** (ou Raccourcis personnalisés)
2. Ajoutez une nouvelle commande : `/chemin/vers/linvoc/.venv/bin/python3 -m src.main`
3. Assignez le raccourci : `Meta+H` (Alt+H sous Windows)

> [!TIP]
> Sur KDE, vous pouvez aussi simplement taper "Raccourcis" dans le menu K.

### GNOME

1. **Paramètres** → **Clavier** → **Raccourcis personnalisés**
2. **+** pour ajouter
3. **Nom** : Dictée vocale
4. **Commande** : `linvoc`
5. **Raccourci** : ex. `Super+H`

### XFCE

1. **Paramètres** → **Clavier** → **Raccourcis d'applications**
2. **Ajouter** : `linvoc` avec le raccourci souhaité

## 🔧 Dépannage

### "nerd-dictation non trouvé"

```bash
pip install git+https://github.com/ideasman42/nerd-dictation.git
nerd-dictation setup-vosk fr
```

### "Aucun backend d'injection"

**X11 :**
```bash
sudo apt install xdotool
```

**Wayland :**
```bash
sudo apt install ydotool
sudo systemctl enable --now ydotool
```

### "Le texte ne s'insère pas"

- Vérifiez que le curseur est bien dans un champ texte **avant** de lancer linvoc
- Sur Wayland, assurez-vous que le daemon ydotoold tourne :
  ```bash
  systemctl status ydotool
  ```

### Latence de la reconnaissance

La reconnaissance vocale prend 2-3 secondes après la fin de la parole. C'est normal avec Vosk en mode offline.

## 📁 Structure du projet

```
linvoc/
├── src/
│   ├── main.py              # Point d'entrée CLI
│   ├── core/
│   │   ├── environment.py   # Détection X11/Wayland
│   │   ├── dictation.py     # Interface nerd-dictation
│   │   └── text_injector.py # Factory backends
│   ├── backends/
│   │   ├── xdotool_backend.py   # X11
│   │   ├── ydotool_backend.py   # Wayland fallback
│   │   └── portal_backend.py    # XDG Portal
│   └── gui/
│       ├── main_window.py   # Widget flottant
│       └── styles.py        # Thème
├── tests/
├── pyproject.toml
└── README.md
```

## 🌍 Langues supportées

linvoc utilise les modèles Vosk. Langues disponibles :

| Code | Langue |
|------|--------|
| `fr` | Français |
| `en` | Anglais |
| `de` | Allemand |
| `es` | Espagnol |
| `it` | Italien |
| `pt` | Portugais |
| `ru` | Russe |
| `zh` | Chinois |

Liste complète : [Vosk Models](https://alphacephei.com/vosk/models)

```bash
# Télécharger un modèle
nerd-dictation setup-vosk <code>

# Lancer avec cette langue
linvoc --lang <code>
```

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
# linvoc
