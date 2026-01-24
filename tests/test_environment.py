"""Tests pour le module de détection d'environnement."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.core.environment import (
    EnvironmentDetector,
    SessionType,
    DesktopEnvironment,
)


class TestSessionTypeDetection:
    """Tests de détection du type de session."""

    def test_detect_x11_from_env(self):
        """Détecte X11 via XDG_SESSION_TYPE."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"}, clear=False):
            assert EnvironmentDetector.get_session_type() == SessionType.X11

    def test_detect_wayland_from_env(self):
        """Détecte Wayland via XDG_SESSION_TYPE."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}, clear=False):
            assert EnvironmentDetector.get_session_type() == SessionType.WAYLAND

    def test_detect_wayland_from_display(self):
        """Détecte Wayland via WAYLAND_DISPLAY."""
        env = {
            "XDG_SESSION_TYPE": "",
            "WAYLAND_DISPLAY": "wayland-0",
            "DISPLAY": "",
        }
        with patch.dict(os.environ, env, clear=False):
            assert EnvironmentDetector.get_session_type() == SessionType.WAYLAND

    def test_detect_x11_from_display(self):
        """Détecte X11 via DISPLAY."""
        env = {
            "XDG_SESSION_TYPE": "",
            "WAYLAND_DISPLAY": "",
            "DISPLAY": ":0",
        }
        with patch.dict(os.environ, env, clear=False):
            assert EnvironmentDetector.get_session_type() == SessionType.X11

    def test_detect_unknown(self):
        """Retourne UNKNOWN si aucune indication."""
        env = {
            "XDG_SESSION_TYPE": "",
            "WAYLAND_DISPLAY": "",
            "DISPLAY": "",
        }
        with patch.dict(os.environ, env, clear=False):
            assert EnvironmentDetector.get_session_type() == SessionType.UNKNOWN


class TestDesktopEnvironmentDetection:
    """Tests de détection de l'environnement de bureau."""

    def test_detect_gnome(self):
        """Détecte GNOME."""
        env = {"XDG_CURRENT_DESKTOP": "GNOME", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.GNOME

    def test_detect_kde(self):
        """Détecte KDE Plasma."""
        env = {"XDG_CURRENT_DESKTOP": "KDE", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.KDE

    def test_detect_plasma(self):
        """Détecte Plasma via le nom."""
        env = {"XDG_CURRENT_DESKTOP": "plasma", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.KDE

    def test_detect_xfce(self):
        """Détecte XFCE."""
        env = {"XDG_CURRENT_DESKTOP": "XFCE", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.XFCE

    def test_detect_cinnamon(self):
        """Détecte Cinnamon."""
        env = {"XDG_CURRENT_DESKTOP": "X-Cinnamon", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.CINNAMON

    def test_detect_hyprland(self):
        """Détecte Hyprland."""
        env = {"XDG_CURRENT_DESKTOP": "Hyprland", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.HYPRLAND

    def test_detect_sway(self):
        """Détecte Sway."""
        env = {"XDG_CURRENT_DESKTOP": "sway", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.SWAY

    def test_detect_unknown_desktop(self):
        """Retourne UNKNOWN pour un DE inconnu."""
        env = {"XDG_CURRENT_DESKTOP": "SomeRandomDE", "DESKTOP_SESSION": ""}
        with patch.dict(os.environ, env, clear=True):
            assert EnvironmentDetector.get_desktop_environment() == DesktopEnvironment.UNKNOWN


class TestToolAvailability:
    """Tests de disponibilité des outils."""

    def test_has_xdotool_when_available(self):
        """xdotool détecté quand présent."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            assert EnvironmentDetector.has_xdotool() is True

    def test_has_xdotool_when_missing(self):
        """xdotool non détecté quand absent."""
        with patch("shutil.which", return_value=None):
            assert EnvironmentDetector.has_xdotool() is False

    def test_has_ydotool_when_available(self):
        """ydotool détecté quand présent."""
        with patch("shutil.which", return_value="/usr/bin/ydotool"):
            assert EnvironmentDetector.has_ydotool() is True

    def test_has_nerd_dictation_when_available(self):
        """nerd-dictation détecté quand présent."""
        with patch("shutil.which", return_value="/usr/bin/nerd-dictation"):
            assert EnvironmentDetector.has_nerd_dictation() is True


class TestRecommendedBackend:
    """Tests de recommandation de backend."""

    def test_recommends_xdotool_on_x11(self):
        """Recommande xdotool sur X11."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"}, clear=False):
            with patch("shutil.which", return_value="/usr/bin/xdotool"):
                with patch.object(EnvironmentDetector, "has_portal_support", return_value=False):
                    assert EnvironmentDetector.get_recommended_backend() == "xdotool"

    def test_recommends_portal_on_wayland(self):
        """Recommande portal sur Wayland si disponible."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}, clear=False):
            with patch.object(EnvironmentDetector, "has_portal_support", return_value=True):
                assert EnvironmentDetector.get_recommended_backend() == "portal"

    def test_recommends_ydotool_fallback_wayland(self):
        """Recommande ydotool comme fallback Wayland."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}, clear=False):
            with patch.object(EnvironmentDetector, "has_portal_support", return_value=False):
                with patch("shutil.which", return_value="/usr/bin/ydotool"):
                    assert EnvironmentDetector.get_recommended_backend() == "ydotool"


class TestEnvironmentInfo:
    """Tests du dictionnaire d'informations."""

    def test_get_environment_info_structure(self):
        """Vérifie la structure du dict retourné."""
        info = EnvironmentDetector.get_environment_info()
        
        assert "session_type" in info
        assert "desktop_environment" in info
        assert "has_portal" in info
        assert "has_xdotool" in info
        assert "has_ydotool" in info
        assert "has_nerd_dictation" in info
        assert "recommended_backend" in info
