"""Backend XDG Desktop Portal pour l'injection de texte (Wayland)."""

import subprocess  # nosec B404 - nécessaire pour les outils CLI
from typing import Optional

from ..core.text_injector import TextInjectorBackend


class PortalBackend(TextInjectorBackend):
    """
    Backend d'injection de texte via XDG Desktop Portal.
    
    Utilise le presse-papier + simulation Ctrl+V car il n'existe pas
    encore d'API Portal standard pour l'injection de texte directe.
    
    Ce backend est préféré sur Wayland car il respecte le modèle
    de sécurité et fonctionne avec les portails du DE.
    """

    def __init__(self):
        """Initialise le backend Portal."""
        self._bus = None
        self._portal = None
        self._clipboard_backup: Optional[str] = None

    @property
    def name(self) -> str:
        """Nom du backend."""
        return "portal"

    def is_available(self) -> bool:
        """
        Vérifie si XDG Desktop Portal est disponible.
        
        Returns:
            bool: True si le portail est accessible
        """
        try:
            import dbus
            bus = dbus.SessionBus()
            bus.get_object(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop"
            )
            return True
        except ImportError:
            # dbus-python non installé
            return False
        except Exception:
            return False

    def _backup_clipboard(self) -> Optional[str]:
        """
        Sauvegarde le contenu actuel du presse-papier.
        
        Returns:
            str ou None: Contenu sauvegardé
        """
        try:
            # Utiliser xclip ou wl-paste selon l'environnement
            result = subprocess.run(  # nosec B603 B607
                ["wl-paste", "--no-newline"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:  # nosec B110 - fallback voulu
            pass
        
        # Fallback xclip (X11/XWayland)
        try:
            result = subprocess.run(  # nosec B603 B607
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:  # nosec B110 - fallback voulu
            pass
        
        return None

    def _restore_clipboard(self, content: str):
        """
        Restaure le contenu du presse-papier.
        
        Args:
            content: Contenu à restaurer
        """
        if not content:
            return
        
        try:
            # wl-copy pour Wayland
            subprocess.run(  # nosec B603 B607
                ["wl-copy", "--"],
                input=content,
                text=True,
                timeout=5,
            )
        except Exception:
            # Fallback xclip
            try:
                subprocess.run(  # nosec B603 B607
                    ["xclip", "-selection", "clipboard"],
                    input=content,
                    text=True,
                    timeout=5,
                )
            except Exception:  # nosec B110 - fallback voulu
                pass

    def _set_clipboard(self, text: str) -> bool:
        """
        Met le texte dans le presse-papier.
        
        Args:
            text: Texte à copier
            
        Returns:
            bool: True si succès
        """
        # Essayer wl-copy d'abord (Wayland natif)
        try:
            result = subprocess.run(  # nosec B603 B607
                ["wl-copy", "--"],
                input=text,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True
        except Exception:  # nosec B110 - fallback voulu
            pass
        
        # Fallback xclip
        try:
            result = subprocess.run(  # nosec B603 B607
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _simulate_paste(self) -> bool:
        """
        Simule Ctrl+V pour coller.
        
        Returns:
            bool: True si succès
        """
        # Essayer ydotool d'abord (Wayland)
        try:
            result = subprocess.run(  # nosec B603 B607
                ["ydotool", "key", "29:1", "47:1", "47:0", "29:0"],  # Ctrl+V
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True
        except Exception:  # nosec B110 - fallback voulu
            pass
        
        # Fallback wtype
        try:
            result = subprocess.run(  # nosec B603 B607
                ["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True
        except Exception:  # nosec B110 - fallback voulu
            pass
        
        # Fallback xdotool (X11/XWayland)
        try:
            result = subprocess.run(  # nosec B603 B607
                ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def inject_text(self, text: str) -> bool:
        """
        Injecte du texte via clipboard + Ctrl+V.
        
        Args:
            text: Texte à injecter
            
        Returns:
            bool: True si l'injection a réussi
        """
        if not text:
            return True
        
        # Sauvegarder le clipboard
        self._clipboard_backup = self._backup_clipboard()
        
        try:
            # Mettre le texte dans le clipboard
            if not self._set_clipboard(text):
                return False
            
            # Petit délai pour que le clipboard soit prêt
            import time
            time.sleep(0.05)
            
            # Simuler Ctrl+V
            success = self._simulate_paste()
            
            # Délai avant restauration
            time.sleep(0.1)
            
            return success
            
        finally:
            # Restaurer le clipboard original après un court délai
            if self._clipboard_backup:
                import threading
                def restore():
                    import time
                    time.sleep(0.5)  # Attendre que le paste soit terminé
                    self._restore_clipboard(self._clipboard_backup)
                threading.Thread(target=restore, daemon=True).start()
