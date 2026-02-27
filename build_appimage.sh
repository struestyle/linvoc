#!/bin/bash
# ──────────────────────────────────────────────────────────────
# build_appimage.sh — Crée un AppImage pour linvoc
# ──────────────────────────────────────────────────────────────
set -euo pipefail

# ── Couleurs ──────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
error() { echo -e "${RED}✗${NC} $*" >&2; }

# ── Répertoires ───────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
DIST_DIR="${SCRIPT_DIR}/dist"
APPIMAGE_DIR="${SCRIPT_DIR}/AppImage"

echo -e "${BOLD}📦 Création d'AppImage pour linvoc${NC}"
echo "   Projet : ${SCRIPT_DIR}"
echo ""

# ── 1. Vérifier PyInstaller ───────────────────────────────────
if ! command -v pyinstaller &>/dev/null; then
    error "pyinstaller est requis. Installez-le : pip install pyinstaller"
    exit 1
fi
info "PyInstaller trouvé"

# ── 2. Vérifier appimagetool ──────────────────────────────────
if ! command -v appimagetool &>/dev/null; then
    warn "appimagetool non trouvé. Installation recommandée :"
    echo "  wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "  chmod +x appimagetool-x86_64.AppImage"
    echo "  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
fi

# ── 3. Nettoyer ───────────────────────────────────────────────
rm -rf "${BUILD_DIR}" "${DIST_DIR}" "${APPIMAGE_DIR}"
mkdir -p "${APPIMAGE_DIR}"

# ── 4. Créer l'exécutable avec PyInstaller ───────────────────
info "Création de l'exécutable..."
pyinstaller --onefile \
    --windowed \
    --name linvoc \
    --add-data "src:src" \
    --hidden-import PySide6 \
    --hidden-import faster_whisper \
    --hidden-import nemo_toolkit \
    --hidden-import spellchecker \
    src/main.py

# ── 5. Préparer la structure AppImage ────────────────────────
info "Préparation de la structure AppImage..."
cp "${DIST_DIR}/linvoc" "${APPIMAGE_DIR}/"
cp "${SCRIPT_DIR}/linvoc.desktop" "${APPIMAGE_DIR}/" 2>/dev/null || true
cp "${SCRIPT_DIR}/assets/icon.png" "${APPIMAGE_DIR}/linvoc.png" 2>/dev/null || true

# Créer linvoc.desktop si manquant
cat > "${APPIMAGE_DIR}/linvoc.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=linvoc
Comment=Dictée vocale pour Linux
Exec=linvoc
Icon=linvoc
Categories=Utility;
DESKTOP

# Créer AppRun
cat > "${APPIMAGE_DIR}/AppRun" << APPRUN
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\${HERE}/usr/bin:\${PATH}"
export LD_LIBRARY_PATH="\${HERE}/usr/lib:\${LD_LIBRARY_PATH}"
exec "\${HERE}/linvoc" "\$@"
APPRUN
chmod +x "${APPIMAGE_DIR}/AppRun"

# ── 6. Générer l'AppImage ────────────────────────────────────
info "Génération de l'AppImage..."
appimagetool "${APPIMAGE_DIR}" "${SCRIPT_DIR}/linvoc.AppImage"

# ── 7. Nettoyer et finaliser ──────────────────────────────────
rm -rf "${BUILD_DIR}" "${DIST_DIR}" "${APPIMAGE_DIR}"

if [ -f "${SCRIPT_DIR}/linvoc.AppImage" ]; then
    info "AppImage créée : ${SCRIPT_DIR}/linvoc.AppImage"
    echo ""
    echo -e "${BOLD}Utilisation :${NC}"
    echo "  chmod +x linvoc.AppImage"
    echo "  ./linvoc.AppImage --help"
else
    error "Échec de la création de l'AppImage"
    exit 1
fi