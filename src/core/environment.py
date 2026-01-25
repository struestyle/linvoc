"""Environment detection for X11/Wayland and desktop environments."""

import os
import shutil
import sys
from enum import Enum
from typing import Optional


class SessionType(Enum):
    """Type de session graphique."""
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class DesktopEnvironment(Enum):
    """Environnement de bureau détecté."""
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    CINNAMON = "cinnamon"
    MATE = "mate"
    LXQT = "lxqt"
    HYPRLAND = "hyprland"
    SWAY = "sway"
    UNKNOWN = "unknown"


class EnvironmentDetector:
    """Détecte l'environnement graphique Linux (X11/Wayland, DE)."""

    @staticmethod
    def get_executable_path(name: str) -> Optional[str]:
        """
        Cherche le chemin absolu d'un exécutable.

        Cherche dans le PATH, puis dans le dossier bin de l'exécutable Python actuel
        (utile si l'environnement virtuel n'est pas activé dans le shell).

        Args:
            name: Nom de l'exécutable

        Returns:
            Optional[str]: Chemin absolu ou None
        """
        # 1. Chercher dans le PATH standard
        path = shutil.which(name)
        if path:
            return path

        # 2. Chercher dans le dossier bin de l'environnement actuel
        # sys.executable pointe vers .venv/bin/python ou /usr/bin/python
        venv_bin_dir = os.path.dirname(sys.executable)
        local_path = shutil.which(name, path=venv_bin_dir)
        if local_path:
            return local_path

        return None


    @staticmethod
    def get_session_type() -> SessionType:
        """
        Détecte le type de session graphique.

        Returns:
            SessionType: X11, WAYLAND ou UNKNOWN
        """
        # Vérifier $XDG_SESSION_TYPE en priorité
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

        if session_type == "wayland":
            return SessionType.WAYLAND
        if session_type == "x11":
            return SessionType.X11

        # Fallback: vérifier les variables d'affichage
        if os.environ.get("WAYLAND_DISPLAY"):
            return SessionType.WAYLAND
        if os.environ.get("DISPLAY"):
            return SessionType.X11

        return SessionType.UNKNOWN

    @staticmethod
    def get_desktop_environment() -> DesktopEnvironment:
        """
        Détecte l'environnement de bureau.

        Returns:
            DesktopEnvironment: Le DE détecté
        """
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()

        # Combiner les deux sources
        combined = f"{desktop} {session}"

        if "gnome" in combined:
            return DesktopEnvironment.GNOME
        if "kde" in combined or "plasma" in combined:
            return DesktopEnvironment.KDE
        if "xfce" in combined:
            return DesktopEnvironment.XFCE
        if "cinnamon" in combined:
            return DesktopEnvironment.CINNAMON
        if "mate" in combined:
            return DesktopEnvironment.MATE
        if "lxqt" in combined:
            return DesktopEnvironment.LXQT
        if "hyprland" in combined:
            return DesktopEnvironment.HYPRLAND
        if "sway" in combined:
            return DesktopEnvironment.SWAY

        return DesktopEnvironment.UNKNOWN

    @staticmethod
    def has_portal_support() -> bool:
        """
        Vérifie si XDG Desktop Portal est disponible.

        Returns:
            bool: True si le portail est disponible
        """
        try:
            import dbus
            bus = dbus.SessionBus()
            bus.get_object(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop"
            )
            return True
        except (ImportError, OSError, AttributeError):
            return False

    @staticmethod
    def has_xdotool() -> bool:
        """Vérifie si xdotool est installé."""
        return EnvironmentDetector.get_executable_path("xdotool") is not None

    @staticmethod
    def has_ydotool() -> bool:
        """Vérifie si ydotool est installé."""
        return EnvironmentDetector.get_executable_path("ydotool") is not None

    @staticmethod
    def has_nerd_dictation() -> bool:
        """Vérifie si nerd-dictation est installé."""
        return EnvironmentDetector.get_executable_path("nerd-dictation") is not None

    @classmethod
    def get_recommended_backend(cls) -> str:
        """
        Retourne le backend d'injection de texte recommandé.

        Returns:
            str: 'portal', 'xdotool', 'ydotool' ou 'none'
        """
        session = cls.get_session_type()

        # Sur Wayland, préférer Portal > ydotool
        if session == SessionType.WAYLAND:
            if cls.has_portal_support():
                return "portal"
            if cls.has_ydotool():
                return "ydotool"

        # Sur X11, préférer xdotool
        if session == SessionType.X11:
            if cls.has_xdotool():
                return "xdotool"

        # Fallbacks génériques
        if cls.has_portal_support():
            return "portal"
        if cls.has_xdotool():
            return "xdotool"
        if cls.has_ydotool():
            return "ydotool"

        return "none"

    @classmethod
    def get_environment_info(cls) -> dict:
        """
        Retourne un dictionnaire avec toutes les infos d'environnement.

        Returns:
            dict: Informations complètes sur l'environnement
        """
        return {
            "session_type": cls.get_session_type().value,
            "desktop_environment": cls.get_desktop_environment().value,
            "has_portal": cls.has_portal_support(),
            "has_xdotool": cls.has_xdotool(),
            "has_ydotool": cls.has_ydotool(),
            "has_nerd_dictation": cls.has_nerd_dictation(),
            "recommended_backend": cls.get_recommended_backend(),
        }
