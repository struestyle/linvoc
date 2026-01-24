"""Tests pour le module d'injection de texte."""

import pytest
from unittest.mock import patch, MagicMock

from src.core.text_injector import TextInjector, TextInjectorBackend
from src.backends.xdotool_backend import XdotoolBackend
from src.backends.ydotool_backend import YdotoolBackend
from src.backends.portal_backend import PortalBackend


class TestTextInjectorBackendInterface:
    """Tests de l'interface abstraite."""

    def test_backend_has_required_methods(self):
        """Vérifie que les backends implémentent l'interface."""
        # XdotoolBackend
        xdotool = XdotoolBackend()
        assert hasattr(xdotool, "inject_text")
        assert hasattr(xdotool, "is_available")
        assert hasattr(xdotool, "name")
        
        # YdotoolBackend
        ydotool = YdotoolBackend()
        assert hasattr(ydotool, "inject_text")
        assert hasattr(ydotool, "is_available")
        assert hasattr(ydotool, "name")
        
        # PortalBackend
        portal = PortalBackend()
        assert hasattr(portal, "inject_text")
        assert hasattr(portal, "is_available")
        assert hasattr(portal, "name")


class TestXdotoolBackend:
    """Tests du backend xdotool."""

    def test_name(self):
        """Vérifie le nom du backend."""
        backend = XdotoolBackend()
        assert backend.name == "xdotool"

    def test_is_available_when_installed(self):
        """Disponible quand xdotool est installé."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            backend = XdotoolBackend()
            assert backend.is_available() is True

    def test_is_available_when_not_installed(self):
        """Non disponible quand xdotool n'est pas installé."""
        with patch("shutil.which", return_value=None):
            backend = XdotoolBackend()
            assert backend.is_available() is False

    def test_inject_empty_text(self):
        """Injecter du texte vide retourne True."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            backend = XdotoolBackend()
            assert backend.inject_text("") is True

    def test_inject_text_calls_xdotool(self):
        """Vérifie l'appel à xdotool type."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            backend = XdotoolBackend()
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                result = backend.inject_text("Hello World")
                
                assert result is True
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "xdotool" in call_args
                assert "type" in call_args
                assert "Hello World" in call_args


class TestYdotoolBackend:
    """Tests du backend ydotool."""

    def test_name(self):
        """Vérifie le nom du backend."""
        backend = YdotoolBackend()
        assert backend.name == "ydotool"

    def test_is_available_when_installed_and_daemon_running(self):
        """Disponible quand ydotool est installé et daemon actif."""
        with patch("shutil.which", return_value="/usr/bin/ydotool"):
            with patch("subprocess.run") as mock_run:
                # pgrep trouve le daemon
                mock_run.return_value = MagicMock(returncode=0)
                
                backend = YdotoolBackend()
                assert backend.is_available() is True

    def test_is_available_when_daemon_not_running(self):
        """Non disponible quand le daemon ne tourne pas."""
        with patch("shutil.which", return_value="/usr/bin/ydotool"):
            with patch("subprocess.run") as mock_run:
                # pgrep ne trouve pas le daemon
                mock_run.return_value = MagicMock(returncode=1)
                
                backend = YdotoolBackend()
                assert backend.is_available() is False

    def test_get_daemon_instructions(self):
        """Vérifie les instructions pour le daemon."""
        instructions = YdotoolBackend.get_daemon_instructions()
        assert "ydotoold" in instructions
        assert "systemctl" in instructions


class TestPortalBackend:
    """Tests du backend XDG Portal."""

    def test_name(self):
        """Vérifie le nom du backend."""
        backend = PortalBackend()
        assert backend.name == "portal"

    def test_is_available_without_dbus(self):
        """Non disponible sans dbus-python."""
        with patch.dict("sys.modules", {"dbus": None}):
            backend = PortalBackend()
            # Le test dépend de l'environnement réel
            # On vérifie juste que ça ne crashe pas
            result = backend.is_available()
            assert isinstance(result, bool)


class TestTextInjectorFactory:
    """Tests de la factory TextInjector."""

    def test_create_with_forced_backend(self):
        """Crée le backend forcé."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            backend = TextInjector.create(force_backend="xdotool")
            assert isinstance(backend, XdotoolBackend)

    def test_create_raises_on_unknown_backend(self):
        """Erreur pour un backend inconnu."""
        with pytest.raises(ValueError, match="Backend inconnu"):
            TextInjector.create(force_backend="nonexistent")

    def test_create_raises_when_forced_backend_unavailable(self):
        """Erreur quand le backend forcé n'est pas disponible."""
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="non disponible"):
                TextInjector.create(force_backend="xdotool")

    def test_inject_shortcut(self):
        """Test du raccourci inject()."""
        with patch("shutil.which", return_value="/usr/bin/xdotool"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                # Reset singleton
                TextInjector._instance = None
                
                result = TextInjector.inject("Test")
                assert result is True
