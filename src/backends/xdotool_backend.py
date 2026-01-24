"""Backend X11 utilisant xdotool pour l'injection de texte."""

import subprocess
import shutil
from typing import Optional

from ..core.text_injector import TextInjectorBackend


class XdotoolBackend(TextInjectorBackend):
    """
    Backend d'injection de texte via xdotool (X11).
    
    Utilise `xdotool type` pour simuler la frappe clavier.
    Fonctionne uniquement sur X11.
    """

    def __init__(self):
        """Initialise le backend xdotool."""
        self._xdotool_path: Optional[str] = shutil.which("xdotool")

    @property
    def name(self) -> str:
        """Nom du backend."""
        return "xdotool"

    def is_available(self) -> bool:
        """
        Vérifie si xdotool est installé.
        
        Returns:
            bool: True si xdotool est disponible
        """
        return self._xdotool_path is not None

    def inject_text(self, text: str) -> bool:
        """
        Injecte du texte via xdotool type.
        
        Args:
            text: Texte à injecter
            
        Returns:
            bool: True si l'injection a réussi
        """
        if not self.is_available():
            return False
        
        if not text:
            return True  # Rien à faire
        
        try:
            # Utiliser xdotool type avec un délai entre les caractères
            # pour une meilleure compatibilité
            result = subprocess.run(
                [self._xdotool_path, "type",
                    "--clearmodifiers",  # Libérer les modificateurs (Ctrl, Alt, etc.)
                    "--delay", "12",      # Délai entre caractères (ms)
                    "--", text
                ],
                capture_output=True,
                text=True,
                timeout=30,  # Timeout de 30s
            )
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("xdotool: timeout lors de l'injection")
            return False
        except Exception as e:
            print(f"xdotool: erreur - {e}")
            return False

    def get_active_window(self) -> Optional[str]:
        """
        Récupère l'ID de la fenêtre active.
        
        Returns:
            str ou None: ID de la fenêtre active
        """
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                [self._xdotool_path, "getactivewindow"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None

    def focus_window(self, window_id: str) -> bool:
        """
        Donne le focus à une fenêtre.
        
        Args:
            window_id: ID de la fenêtre
            
        Returns:
            bool: True si succès
        """
        if not self.is_available():
            return False
        
        try:
            result = subprocess.run(
                [self._xdotool_path, "windowactivate", "--sync", window_id],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False
