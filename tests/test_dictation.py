"""Tests pour le module de dictée vocale."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import subprocess

from src.core.dictation import DictationManager, DictationState, get_dictation_manager


class TestDictationState:
    """Tests des états de dictée."""

    def test_states_exist(self):
        """Vérifie que tous les états existent."""
        assert DictationState.IDLE.value == "idle"
        assert DictationState.RECORDING.value == "recording"
        assert DictationState.PROCESSING.value == "processing"
        assert DictationState.ERROR.value == "error"


class TestDictationManager:
    """Tests du gestionnaire de dictée."""

    def test_initial_state_is_idle(self):
        """L'état initial est IDLE."""
        manager = DictationManager()
        assert manager.state == DictationState.IDLE

    def test_language_default_is_french(self):
        """La langue par défaut est le français."""
        manager = DictationManager()
        assert manager.language == "fr"

    def test_language_can_be_set(self):
        """La langue peut être configurée."""
        manager = DictationManager(language="en")
        assert manager.language == "en"

    def test_state_change_callback(self):
        """Le callback de changement d'état est appelé."""
        states_received = []
        
        def callback(state):
            states_received.append(state)
        
        manager = DictationManager(on_state_change=callback)
        manager.state = DictationState.RECORDING
        
        assert DictationState.RECORDING in states_received

    def test_state_change_not_called_if_same(self):
        """Le callback n'est pas appelé si l'état est le même."""
        call_count = [0]
        
        def callback(state):
            call_count[0] += 1
        
        manager = DictationManager(on_state_change=callback)
        manager.state = DictationState.IDLE  # Même état
        
        assert call_count[0] == 0

    def test_get_model_path(self):
        """Vérifie la construction du chemin du modèle."""
        manager = DictationManager(language="fr")
        path = manager.get_model_path()
        
        assert "vosk" in path.lower() or "fr" in path.lower()

    def test_is_model_available_false_when_missing(self):
        """is_model_available retourne False si le modèle n'existe pas."""
        with patch("os.path.isdir", return_value=False):
            manager = DictationManager()
            assert manager.is_model_available() is False

    def test_start_returns_false_if_already_recording(self):
        """start() retourne False si déjà en enregistrement."""
        manager = DictationManager()
        manager._state = DictationState.RECORDING
        
        assert manager.start() is False

    def test_start_fails_without_nerd_dictation(self):
        """start() échoue si nerd-dictation n'est pas trouvé."""
        manager = DictationManager()
        
        with patch("subprocess.Popen", side_effect=FileNotFoundError()):
            result = manager.start()
            
            assert result is False
            assert manager.state == DictationState.ERROR

    def test_stop_returns_empty_if_not_recording(self):
        """stop() retourne une chaîne vide si pas en enregistrement."""
        manager = DictationManager()
        assert manager.stop() == ""

    def test_toggle_starts_when_idle(self):
        """toggle() démarre l'enregistrement quand IDLE."""
        manager = DictationManager()
        
        with patch.object(manager, "start", return_value=True) as mock_start:
            result = manager.toggle()
            
            mock_start.assert_called_once()
            assert result is None

    def test_toggle_stops_when_recording(self):
        """toggle() arrête l'enregistrement quand RECORDING."""
        manager = DictationManager()
        manager._state = DictationState.RECORDING
        
        with patch.object(manager, "stop", return_value="Texte test") as mock_stop:
            result = manager.toggle()
            
            mock_stop.assert_called_once()
            assert result == "Texte test"


class TestDictationManagerIntegration:
    """Tests d'intégration (nécessitent nerd-dictation)."""

    @pytest.mark.skipif(
        not DictationManager().is_model_available(),
        reason="Modèle Vosk non disponible"
    )
    def test_start_stop_cycle(self):
        """Test d'un cycle complet start/stop."""
        manager = DictationManager()
        
        # Ce test ne peut fonctionner que si nerd-dictation est installé
        # et un modèle est disponible
        try:
            started = manager.start()
            if started:
                import time
                time.sleep(0.5)
                text = manager.stop()
                assert isinstance(text, str)
        except FileNotFoundError:
            pytest.skip("nerd-dictation non installé")


class TestGetDictationManager:
    """Tests du singleton."""

    def test_returns_same_instance(self):
        """get_dictation_manager retourne la même instance."""
        # Reset le singleton
        import src.core.dictation as dictation_module
        dictation_module._dictation_manager = None
        
        manager1 = get_dictation_manager()
        manager2 = get_dictation_manager()
        
        assert manager1 is manager2

    def test_accepts_kwargs_on_first_call(self):
        """Les kwargs sont passés au constructeur."""
        import src.core.dictation as dictation_module
        dictation_module._dictation_manager = None
        
        manager = get_dictation_manager(language="en")
        
        assert manager.language == "en"
