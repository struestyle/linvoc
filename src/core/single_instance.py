"""Gestion d'instance unique pour linvoc."""

import os
import signal
import tempfile
from pathlib import Path

DEFAULT_SCOPE = "linvoc"


def _lock_file(scope: str) -> Path:
    safe_scope = scope.replace(os.sep, "_")
    return Path(tempfile.gettempdir()) / f"{safe_scope}.lock"


def get_running_pid(scope: str = DEFAULT_SCOPE) -> int | None:
    """
    Retourne le PID de l'instance en cours si elle existe.

    Returns:
        int | None: PID si une instance est en cours, None sinon
    """
    lock_file = _lock_file(scope)
    if not lock_file.exists():
        return None

    try:
        pid = int(lock_file.read_text().strip())
        # Vérifie si le processus existe toujours
        os.kill(pid, 0)
        return pid
    except (ValueError, ProcessLookupError, PermissionError):
        # PID invalide ou processus mort
        lock_file.unlink(missing_ok=True)
        return None


def create_lock(scope: str = DEFAULT_SCOPE):
    """Crée le fichier lock avec le PID actuel."""
    _lock_file(scope).write_text(str(os.getpid()))


def remove_lock(scope: str = DEFAULT_SCOPE):
    """Supprime le fichier lock."""
    _lock_file(scope).unlink(missing_ok=True)


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
