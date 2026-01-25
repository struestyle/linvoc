"""Backend Wayland utilisant ydotool pour l'injection de texte."""

import subprocess  # nosec B404 - nécessaire pour ydotool
from typing import Optional

from ..core.text_injector import TextInjectorBackend
from ..core.environment import EnvironmentDetector


class YdotoolBackend(TextInjectorBackend):
    """
    Backend d'injection de texte via ydotool (Wayland).

    Utilise `ydotool type` pour simuler la frappe clavier.
    Nécessite que le daemon ydotoold soit en cours d'exécution.
    """

    def __init__(self):
        """Initialise le backend ydotool."""
        self._ydotool_path: Optional[str] = EnvironmentDetector.get_executable_path("ydotool")
        self._pgrep_path: Optional[str] = EnvironmentDetector.get_executable_path("pgrep")

    @property
    def name(self) -> str:
        """Nom du backend."""
        return "ydotool"

    def is_available(self) -> bool:
        """
        Vérifie si ydotool est installé et le daemon actif.

        Returns:
            bool: True si ydotool est disponible
        """
        if self._ydotool_path is None:
            return False

        # Vérifier que le daemon tourne
        return self._is_daemon_running()

    def _is_daemon_running(self) -> bool:
        """
        Vérifie si ydotoold est en cours d'exécution.

        Returns:
            bool: True si le daemon est actif
        """
        try:
            pgrep = self._pgrep_path or "pgrep"
            result = subprocess.run(  # nosec B603
                [pgrep, "-x", "ydotoold"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def inject_text(self, text: str) -> bool:
        """
        Injecte du texte via ydotool type.

        Args:
            text: Texte à injecter

        Returns:
            bool: True si l'injection a réussi
        """
        if not self.is_available():
            return False

        if not text:
            return True

        try:
            # ydotool type avec délai entre caractères
            result = subprocess.run(  # nosec B603
                [
                    self._ydotool_path,
                    "type",
                    "--key-delay", "12",  # Délai en ms
                    "--", text
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("ydotool: timeout lors de l'injection")
            return False
        except (OSError, subprocess.SubprocessError) as e:
            print(f"ydotool: erreur - {e}")
            return False

    @staticmethod
    def get_daemon_instructions() -> str:
        """
        Retourne les instructions pour démarrer le daemon.

        Returns:
            str: Instructions utilisateur
        """
        return """
Pour utiliser ydotool, le daemon ydotoold doit être actif:

1. Démarrer le daemon:
   sudo systemctl enable --now ydotool

2. Ajouter votre utilisateur au groupe (si nécessaire):
   sudo usermod -aG ydotool $USER

3. Se déconnecter/reconnecter pour appliquer les changements.
"""
