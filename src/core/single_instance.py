"""Gestion d'instance unique pour linvoc."""

import os
import signal
import tempfile
from pathlib import Path

LOCK_FILE = Path(tempfile.gettempdir()) / "linvoc.lock"


def get_running_pid() -> int | None:
    """
    Retourne le PID de l'instance en cours si elle existe.

    Returns:
        int | None: PID si une instance est en cours, None sinon
    """
    if not LOCK_FILE.exists():
        return None

    try:
        pid = int(LOCK_FILE.read_text().strip())
        # Vérifie si le processus existe toujours
        os.kill(pid, 0)
        return pid
    except (ValueError, ProcessLookupError, PermissionError):
        # PID invalide ou processus mort
        LOCK_FILE.unlink(missing_ok=True)
        return None


def create_lock():
    """Crée le fichier lock avec le PID actuel."""
    LOCK_FILE.write_text(str(os.getpid()))


def remove_lock():
    """Supprime le fichier lock."""
    LOCK_FILE.unlink(missing_ok=True)


def send_toggle_signal(pid: int) -> bool:
    """
    Envoie le signal SIGUSR1 au processus pour toggle la dictée.

    Args:
        pid: PID du processus cible

    Returns:
        bool: True si le signal a été envoyé avec succès
    """
    try:
        os.kill(pid, signal.SIGUSR1)
        return True
    except (ProcessLookupError, PermissionError):
        return False
