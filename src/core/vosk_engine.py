"""Moteur de reconnaissance vocale basé sur VOSK via nerd-dictation."""

import subprocess  # nosec B404 - nécessaire pour nerd-dictation
import os
import sys
from typing import Optional, Callable

from .engine_base import SpeechEngine, EngineType, DictationState
from .environment import EnvironmentDetector


class VoskEngine(SpeechEngine):
    """
    Moteur de reconnaissance vocale basé sur VOSK via nerd-dictation.

    Utilise nerd-dictation comme subprocess pour la reconnaissance vocale
    offline avec une latence très faible (streaming).
    """

    # Chemins par défaut des modèles Vosk
    DEFAULT_MODEL_DIRS = [
        os.path.expanduser("~/.config/nerd-dictation/model"),
        os.path.expanduser("~/.local/share/vosk"),
    ]

    def __init__(
        self,
        language: str = "fr",
        model_dir: Optional[str] = None,
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        """
        Initialise le moteur VOSK.

        Args:
            language: Code langue ('fr', 'en', etc.)
            model_dir: Répertoire spécifique des modèles (optionnel)
            on_text: Callback appelé quand du texte est reconnu
            on_state_change: Callback appelé lors des changements d'état
        """
        super().__init__(language, on_text, on_state_change)
        self.model_dir = model_dir
        self._process: Optional[subprocess.Popen] = None

    @property
    def engine_type(self) -> EngineType:
        """Retourne le type de moteur."""
        return EngineType.VOSK

    def get_model_path(self) -> str:
        """
        Retourne le chemin du modèle Vosk pour la langue configurée.

        Returns:
            str: Chemin vers le modèle
        """
        # 1. Si un chemin spécifique est fourni
        if self.model_dir and os.path.isdir(self.model_dir):
            return self.model_dir

        # 2. Chercher dans les dossiers par défaut
        for base_dir in self.DEFAULT_MODEL_DIRS:
            if not os.path.isdir(base_dir):
                continue

            # Si le dossier est directement le modèle (cas ~/.config/nerd-dictation/model)
            if "vosk-model" in base_dir or self.language in base_dir:
                return base_dir

            # Chercher un sous-dossier correspondant à la langue
            for entry in os.listdir(base_dir):
                full_path = os.path.join(base_dir, entry)
                if os.path.isdir(full_path) and self.language in entry.lower():
                    return full_path

            # Si le dossier contient directement les fichiers du modèle
            if os.path.exists(os.path.join(base_dir, "am/final.mdl")):
                return base_dir

        # 3. Fallback: chemin par défaut
        return os.path.expanduser("~/.config/nerd-dictation/model")

    def is_model_available(self) -> bool:
        """Vérifie si le modèle vocal est disponible."""
        return os.path.isdir(self.get_model_path())

    def is_available(self) -> bool:
        """
        Vérifie si le moteur VOSK est disponible.

        Returns:
            bool: True si nerd-dictation est installé et le modèle disponible
        """
        return (
            EnvironmentDetector.has_nerd_dictation() and
            self.is_model_available()
        )

    def start(self) -> bool:
        """
        Démarre l'enregistrement vocal via nerd-dictation.

        Returns:
            bool: True si le démarrage a réussi
        """
        if self._state == DictationState.RECORDING:
            return False

        model_path = self.get_model_path()
        nerd_dictation_path = EnvironmentDetector.get_executable_path("nerd-dictation")

        if not nerd_dictation_path:
            print("ERREUR: nerd-dictation non trouvé")
            self.state = DictationState.ERROR
            return False

        cmd = [
            sys.executable,
            nerd_dictation_path,
            "begin",
            "--vosk-model-dir", model_path,
            "--config", "",  # Ignorer les scripts de config locaux
            "--output", "SIMULATE_INPUT",
            "--simulate-input-tool", "XDOTOOL",
            "--verbose", "1"
        ]

        try:
            self._process = subprocess.Popen(  # nosec B603
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )

            self.state = DictationState.RECORDING
            return True
        except (OSError, subprocess.SubprocessError) as e:
            print(f"ERREUR Lancement: {e}")
            self.state = DictationState.ERROR
            return False

    def stop(self) -> str:
        """
        Arrête proprement le processus nerd-dictation.

        Returns:
            str: Texte vide (pour la confidentialité)
        """
        if self._state != DictationState.RECORDING:
            return ""

        self.state = DictationState.PROCESSING

        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    self._process.kill()
                except (ProcessLookupError, OSError):
                    pass  # Processus déjà terminé
            finally:
                self._process = None

        self.state = DictationState.IDLE
        return ""  # On ne retourne rien pour la confidentialité
