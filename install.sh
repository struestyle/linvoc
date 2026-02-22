#!/bin/bash
# ──────────────────────────────────────────────────────────────
# install.sh — Installe linvoc dans ~/.local/bin/
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
INSTALL_DIR="${HOME}/.local/bin"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo -e "${BOLD}🎤 Installation de linvoc${NC}"
echo "   Projet : ${SCRIPT_DIR}"
echo "   Cible  : ${INSTALL_DIR}/linvoc"
echo ""

# ── 1. Vérifier Python ───────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    error "python3 est requis mais n'est pas installé."
    exit 1
fi
info "Python trouvé : $(python3 --version)"

# ── 2. Créer/réparer le venv ──────────────────────────────────
VENV_PYTHON=""
for name in python3 python; do
    if [ -x "${VENV_DIR}/bin/${name}" ] && "${VENV_DIR}/bin/${name}" --version &>/dev/null; then
        VENV_PYTHON="${VENV_DIR}/bin/${name}"
        break
    fi
done

if [ -z "${VENV_PYTHON}" ]; then
    if [ -d "${VENV_DIR}" ]; then
        warn "Environnement virtuel existant mais cassé, recréation..."
        rm -rf "${VENV_DIR}"
    fi
    info "Création de l'environnement virtuel..."
    python3 -m venv "${VENV_DIR}"
    # Trouver le python dans le nouveau venv
    for name in python3 python; do
        if [ -x "${VENV_DIR}/bin/${name}" ]; then
            VENV_PYTHON="${VENV_DIR}/bin/${name}"
            break
        fi
    done
else
    info "Environnement virtuel existant et fonctionnel."
fi

# ── 3. Installer linvoc dans le venv ─────────────────────────
info "Installation des dépendances Python..."
"${VENV_PYTHON}" -m pip install --upgrade pip --quiet
"${VENV_PYTHON}" -m pip install -e "${SCRIPT_DIR}" --quiet
info "Dépendances installées."

# ── 4. Créer ~/.local/bin si nécessaire ───────────────────────
mkdir -p "${INSTALL_DIR}"

# ── 5. Créer le wrapper dans ~/.local/bin ─────────────────────
cat > "${INSTALL_DIR}/linvoc" << WRAPPER
#!/bin/bash
# Wrapper auto-généré par install.sh — $(date +%Y-%m-%d)
# Projet source : ${SCRIPT_DIR}
exec "${VENV_PYTHON}" -c "from src.main import main; import sys; main()" "\$@"
WRAPPER
chmod +x "${INSTALL_DIR}/linvoc"
info "Wrapper installé dans ${INSTALL_DIR}/linvoc"

# ── 6. Vérifier que ~/.local/bin est dans le PATH ─────────────
if ! echo "${PATH}" | tr ':' '\n' | grep -q "${INSTALL_DIR}"; then
    warn "${INSTALL_DIR} n'est pas dans votre PATH."
    echo ""
    echo "  Ajoutez cette ligne à votre ~/.bashrc ou ~/.zshrc :"
    echo ""
    echo "    export PATH=\"\${HOME}/.local/bin:\${PATH}\""
    echo ""
    echo "  Puis rechargez votre shell : source ~/.bashrc"
else
    info "${INSTALL_DIR} est déjà dans le PATH."
fi

# ── 7. Vérification rapide ────────────────────────────────────
echo ""
if "${VENV_PYTHON}" -c "from src.main import main; print('ok')" &>/dev/null; then
    info "Installation réussie ! Lancez ${BOLD}linvoc${NC} depuis n'importe où."
else
    warn "Le wrapper est installé, mais la vérification de l'import a échoué."
    warn "Essayez : ${INSTALL_DIR}/linvoc --check"
fi

echo ""
echo -e "${BOLD}Utilisation :${NC}"
echo "  linvoc              # Lancement standard"
echo "  linvoc --start      # Lancement + écoute immédiate"
echo "  linvoc --check      # Vérification des dépendances"
