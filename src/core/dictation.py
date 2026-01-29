"""Gestionnaire de dictée vocale unifié."""

from typing import Optional, Callable

from .engine_base import SpeechEngine, EngineType, DictationState


class DictationManager:
    """
    Gestionnaire unifié des moteurs de reconnaissance vocale.

    Fournit une interface unifiée pour utiliser VOSK ou Whisper
    comme moteur de reconnaissance vocale.
    """

    def __init__(
        self,
        engine_type: str = "vosk",
        language: str = "fr",
        model_dir: Optional[str] = None,
        model_size: str = "base",
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        """
        Initialise le gestionnaire de dictée.

        Args:
            engine_type: Type de moteur ('vosk' ou 'whisper')
            language: Code langue ('fr', 'en', etc.)
            model_dir: Répertoire spécifique des modèles (optionnel, VOSK uniquement)
            model_size: Taille du modèle Whisper ('tiny', 'base', 'small', etc.)
            on_text: Callback appelé quand du texte est reconnu
            on_state_change: Callback appelé lors des changements d'état
        """
        self._engine_type_str = engine_type
        self.on_state_change = on_state_change
        self._engine = self._create_engine(
            engine_type=engine_type,
            language=language,
            model_dir=model_dir,
            model_size=model_size,
            on_text=on_text,
            on_state_change=on_state_change,
        )

    def _create_engine(
        self,
        engine_type: str,
        language: str,
        model_dir: Optional[str],
        model_size: str,
        on_text: Optional[Callable[[str], None]],
        on_state_change: Optional[Callable[[DictationState], None]],
    ) -> SpeechEngine:
        """
        Factory pour créer le moteur approprié.

        Args:
            engine_type: Type de moteur ('vosk' ou 'whisper')
            language: Code langue
            model_dir: Répertoire des modèles (VOSK)
            model_size: Taille du modèle (Whisper)
            on_text: Callback texte
            on_state_change: Callback état

        Returns:
            SpeechEngine: Instance du moteur
        """
        if engine_type == "whisper":
            from .whisper_engine import WhisperEngine  # pylint: disable=import-outside-toplevel
            return WhisperEngine(
                language=language,
                model_size=model_size,
                on_text=on_text,
                on_state_change=on_state_change,
            )
        else:
            from .vosk_engine import VoskEngine  # pylint: disable=import-outside-toplevel
            return VoskEngine(
                language=language,
                model_dir=model_dir,
                on_text=on_text,
                on_state_change=on_state_change,
            )

    @property
    def state(self) -> DictationState:
        """État actuel de la dictée."""
        return self._engine.state

    @property
    def engine_type(self) -> EngineType:
        """Type de moteur utilisé."""
        return self._engine.engine_type

    @property
    def engine_type_name(self) -> str:
        """Nom du type de moteur (pour affichage)."""
        return self._engine.engine_type.value.upper()

    def is_model_available(self) -> bool:
        """Vérifie si le modèle vocal est disponible."""
        return self._engine.is_available()

    def start(self) -> bool:
        """
        Démarre l'enregistrement vocal.

        Returns:
            bool: True si le démarrage a réussi
        """
        return self._engine.start()

    def stop(self) -> str:
        """
        Arrête l'enregistrement vocal.

        Returns:
            str: Texte reconnu (vide pour la confidentialité)
        """
        return self._engine.stop()

    def toggle(self) -> Optional[str]:
        """Bascule entre démarrage et arrêt."""
        return self._engine.toggle()


# Singleton pour usage global
_DICTATION_MANAGER: Optional[DictationManager] = None


def get_dictation_manager(**kwargs) -> DictationManager:
    """
    Retourne l'instance singleton du gestionnaire de dictée.

    Args:
        **kwargs: Arguments passés au constructeur si création

    Returns:
        DictationManager: Instance du gestionnaire
    """
    global _DICTATION_MANAGER  # pylint: disable=global-statement
    if _DICTATION_MANAGER is None:
        _DICTATION_MANAGER = DictationManager(**kwargs)
    return _DICTATION_MANAGER
