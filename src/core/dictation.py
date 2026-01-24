"""Gestionnaire de dictée vocale via nerd-dictation."""

import subprocess
import threading
import queue
import signal
import os
import shutil
import sys
from typing import Optional, Callable
from enum import Enum

from .environment import EnvironmentDetector


class DictationState(Enum):
    """État du gestionnaire de dictée."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


class DictationManager:
    """
    Gère l'interaction avec nerd-dictation en subprocess.
    
    Utilise nerd-dictation pour la reconnaissance vocale offline via Vosk.
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
        Initialise le gestionnaire de dictée.
        
        Args:
            language: Code langue ('fr', 'en', etc.)
            model_dir: Répertoire spécifique des modèles (optionnel)
            on_text: Callback appelé quand du texte est reconnu
            on_state_change: Callback appelé lors des changements d'état
        """
        self.language = language
        self.model_dir = model_dir
        self.on_text = on_text
        self.on_state_change = on_state_change
        
        self._process: Optional[subprocess.Popen] = None
        self._output_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None
        self._state = DictationState.IDLE
        self._accumulated_text: list[str] = []

    @property
    def state(self) -> DictationState:
        """État actuel de la dictée."""
        return self._state

    @state.setter
    def state(self, new_state: DictationState):
        """Change l'état et notifie le callback."""
        if self._state != new_state:
            self._state = new_state
            if self.on_state_change:
                self.on_state_change(new_state)

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
        return os.path.expanduser(f"~/.config/nerd-dictation/model")

    def is_model_available(self) -> bool:
        """Vérifie si le modèle vocal est disponible."""
        return os.path.isdir(self.get_model_path())

    def start(self) -> bool:
        """
        Démarre l'enregistrement vocal.
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
            nerd_dictation_path,
            "begin",
            "--vosk-model-dir", model_path,
            "--config", "",  # Ignorer les scripts de config locaux
            "--output", "SIMULATE_INPUT",
            "--simulate-input-tool", "XDOTOOL",
            "--verbose", "1"
        ]
        
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, # Retour au silence pour la vie privée
                preexec_fn=os.setsid
            )
            
            self.state = DictationState.RECORDING
            return True
        except Exception as e:
            print(f"ERREUR Lancement: {e}")
            self.state = DictationState.ERROR
            return False

    def stop(self) -> str:
        """Arrête proprement le processus."""
        if self._state != DictationState.RECORDING:
            return ""
        
        self.state = DictationState.PROCESSING
        
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try: self._process.kill()
                except: pass
            finally:
                self._process = None
        
        self.state = DictationState.IDLE
        return "" # On ne retourne rien pour la confidentialité

    def toggle(self) -> Optional[str]:
        if self._state == DictationState.RECORDING:
            return self.stop()
        else:
            self.start()
            return None


# Singleton pour usage global
_dictation_manager: Optional[DictationManager] = None


def get_dictation_manager(**kwargs) -> DictationManager:
    """
    Retourne l'instance singleton du gestionnaire de dictée.
    
    Args:
        **kwargs: Arguments passés au constructeur si création
        
    Returns:
        DictationManager: Instance du gestionnaire
    """
    global _dictation_manager
    if _dictation_manager is None:
        _dictation_manager = DictationManager(**kwargs)
    return _dictation_manager
