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

Il est recommandé d'utiliser un environnement virtuel.

```bash
# Cloner le dépôt
git clone https://github.com/louis/linvoc.git
cd linvoc

# Installer linvoc et ses dépendances Python
pip install -e .
```

> [!NOTE]
> Cette commande installe également `nerd-dictation` et `PySide6`. Si la commande `linvoc` n'est pas reconnue après l'installation, assurez-vous que le dossier `bin` de votre environnement Python est dans votre `PATH`.

### 3. Téléchargement du modèle vocal (Vosk)

`nerd-dictation` nécessite un modèle Vosk pour fonctionner en mode hors-ligne.

```bash
# Créer le dossier de configuration
mkdir -p ~/.config/nerd-dictation
cd ~/.config/nerd-dictation

# Télécharger le modèle français (petit et efficace)
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
mv vosk-model-small-fr-0.22 model
rm vosk-model-small-fr-0.22.zip
```

## 🚀 Utilisation

### Lancement

Si vous avez installé le package avec `pip install -e .`, vous pouvez lancer :

```bash
linvoc                # Lancement standard
linvoc --lang en      # Si vous avez un modèle anglais dans ~/.config/nerd-dictation/model-en
linvoc --check        # Vérification des dépendances
```

> [!TIP]
> Si la commande `linvoc` n'est pas trouvée, vous pouvez tester avec :
> `python3 -m src.main`

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
