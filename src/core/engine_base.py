"""Interface abstraite pour les moteurs de reconnaissance vocale."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Callable


class EngineType(Enum):
    """Types de moteurs de reconnaissance vocale disponibles."""
    VOSK = "vosk"
    WHISPER = "whisper"
    PARAKEET = "parakeet"


class DictationState(Enum):
    """État du gestionnaire de dictée."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


class SpeechEngine(ABC):
    """
    Interface abstraite pour les moteurs de reconnaissance vocale.

    Tous les moteurs (VOSK, Whisper, etc.) doivent implémenter cette interface
    pour être utilisables par le DictationManager.
    """

    def __init__(
        self,
        language: str = "fr",
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        """
        Initialise le moteur de reconnaissance.

        Args:
            language: Code langue ('fr', 'en', etc.)
            on_text: Callback appelé quand du texte est reconnu
            on_state_change: Callback appelé lors des changements d'état
        """
        self.language = language
        self.on_text = on_text
        self.on_state_change = on_state_change
        self._state = DictationState.IDLE

    @property
    def state(self) -> DictationState:
        """État actuel du moteur."""
        return self._state

    @state.setter
    def state(self, new_state: DictationState):
        """Change l'état et notifie le callback."""
        if self._state != new_state:
            self._state = new_state
            if self.on_state_change:
                self.on_state_change(new_state)

    @property
    @abstractmethod
    def engine_type(self) -> EngineType:
        """Retourne le type de moteur."""
        pass

    @abstractmethod
    def start(self) -> bool:
        """
        Démarre la reconnaissance vocale.

        Returns:
            bool: True si le démarrage a réussi
        """
        pass

    @abstractmethod
    def stop(self) -> str:
        """
        Arrête la reconnaissance vocale.

        Returns:
            str: Texte reconnu (vide pour des raisons de confidentialité)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Vérifie si le moteur est disponible et fonctionnel.

        Returns:
            bool: True si le moteur peut être utilisé
        """
        pass

    def toggle(self) -> Optional[str]:
        """Bascule entre démarrage et arrêt."""
        if self._state == DictationState.RECORDING:
            return self.stop()
        self.start()
        return None
