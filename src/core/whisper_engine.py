"""Moteur de reconnaissance vocale basé sur Whisper via pywhispercpp."""

import os
import threading
import tempfile
import wave
from typing import Optional, Callable

from .engine_base import SpeechEngine, EngineType, DictationState
from .text_injector import TextInjector


class WhisperEngine(SpeechEngine):
    """
    Moteur de reconnaissance vocale basé sur Whisper via pywhispercpp.

    Utilise la bibliothèque pywhispercpp pour la transcription audio
    avec une excellente précision. Fonctionne par segments audio
    (latence plus élevée que VOSK mais meilleure reconnaissance).
    """

    # Chemins par défaut des modèles Whisper
    DEFAULT_MODEL_DIRS = [
        os.path.expanduser("~/.local/share/whisper.cpp/models"),
        os.path.expanduser("~/whisper.cpp/models"),
        os.path.expanduser("~/.cache/whisper"),
    ]

    # Paramètres audio
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    TRANSCRIBE_INTERVAL_SECONDS = 2

    # Marqueurs non-verbaux à filtrer (Whisper les génère pour le bruit de fond)
    NON_SPEECH_MARKERS = [
        "[Musique]", "[Music]", "[MUSIC]",
        "[Applaudissements]", "[Applause]", "[APPLAUSE]",
        "[Rires]", "[Laughter]", "[LAUGHTER]",
        "[Bruit]", "[Noise]", "[NOISE]",
        "[Silence]", "[SILENCE]",
        "[Inaudible]", "[INAUDIBLE]",
        "(Musique)", "(Music)",
        "*Musique*", "*Music*",
        "...",
    ]

    def __init__(
        self,
        language: str = "fr",
        model_size: str = "base",
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        """
        Initialise le moteur Whisper.

        Args:
            language: Code langue ('fr', 'en', etc.)
            model_size: Taille du modèle ('tiny', 'base', 'small', 'medium', 'large')
            on_text: Callback appelé quand du texte est reconnu
            on_state_change: Callback appelé lors des changements d'état
        """
        super().__init__(language, on_text, on_state_change)
        self._model_size = model_size
        self._model = None
        self._recording = False
        self._audio_thread: Optional[threading.Thread] = None
        self._injector: Optional[TextInjector] = None
        self._frames: list = []

    @property
    def engine_type(self) -> EngineType:
        """Retourne le type de moteur."""
        return EngineType.WHISPER

    def is_available(self) -> bool:
        """
        Vérifie si pywhispercpp est installé et fonctionnel.

        Returns:
            bool: True si le moteur peut être utilisé
        """
        try:
            from pywhispercpp.model import Model  # pylint: disable=import-outside-toplevel,unused-import
            return True
        except ImportError:
            return False

    def _get_injector(self) -> Optional[TextInjector]:
        """Retourne l'injecteur de texte (lazy loading)."""
        if self._injector is None:
            try:
                self._injector = TextInjector.get_instance()
            except RuntimeError:
                pass
        return self._injector

    def _load_model(self) -> bool:
        """
        Charge le modèle Whisper (téléchargement auto si nécessaire).

        Returns:
            bool: True si le modèle est chargé avec succès
        """
        if self._model is not None:
            return True

        try:
            from pywhispercpp.model import Model  # pylint: disable=import-outside-toplevel

            # Le modèle sera téléchargé automatiquement par pywhispercpp
            # Note: le filtrage des tokens non-verbaux se fait dans _filter_non_speech()
            self._model = Model(
                self._model_size,
                print_realtime=False,
                print_progress=False,
            )
            return True
        except Exception as e:  # pylint: disable=broad-except
            print(f"ERREUR Chargement modèle Whisper: {e}")
            return False

    def start(self) -> bool:
        """
        Démarre la capture audio et la transcription Whisper.

        Returns:
            bool: True si le démarrage a réussi
        """
        if self._recording:
            return False

        if not self.is_available():
            print("ERREUR: pywhispercpp non installé")
            self.state = DictationState.ERROR
            return False

        # Charger le modèle si nécessaire
        if not self._load_model():
            self.state = DictationState.ERROR
            return False

        self._recording = True
        self._audio_thread = threading.Thread(
            target=self._record_and_transcribe,
            daemon=True
        )
        self._audio_thread.start()

        self.state = DictationState.RECORDING
        return True

    def stop(self) -> str:
        """
        Arrête la capture audio et lance la transcription.

        Returns:
            str: Texte vide (pour la confidentialité)
        """
        if not self._recording:
            return ""

        self.state = DictationState.PROCESSING
        self._recording = False

        # Attendre la fin du thread audio (qui va stocker les frames dans self._frames)
        if self._audio_thread and self._audio_thread.is_alive():
            self._audio_thread.join(timeout=30)  # Timeout plus long pour longues dictées

        # Transcrire l'audio accumulé
        if self._frames:
            self._transcribe_and_inject(self._frames)
            self._frames = []

        self.state = DictationState.IDLE
        return ""

    def _record_and_transcribe(self):
        """
        Thread principal de capture audio.

        Capture l'audio du microphone en continu et stocke les frames.
        La transcription se fait à l'arrêt dans stop().
        """
        try:
            import pyaudio  # pylint: disable=import-outside-toplevel
        except ImportError:
            print("ERREUR: PyAudio non installé")
            self.state = DictationState.ERROR
            self._recording = False
            return

        p = pyaudio.PyAudio()

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
        except OSError as e:
            print(f"ERREUR Ouverture microphone: {e}")
            p.terminate()
            self.state = DictationState.ERROR
            self._recording = False
            return

        self._frames = []

        try:
            while self._recording:
                try:
                    data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    self._frames.append(data)
                except OSError:
                    # Overflow ou erreur de lecture, continuer
                    continue

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def _transcribe_and_inject(self, frames: list):
        """
        Transcrit les frames audio et injecte le texte reconnu.

        Args:
            frames: Liste des frames audio à transcrire
        """
        if not frames or self._model is None:
            return

        # Créer un fichier WAV temporaire
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(b''.join(frames))

            # Transcrire avec Whisper
            try:
                segments = self._model.transcribe(
                    temp_file.name,
                    language=self.language,
                )

                for segment in segments:
                    text = segment.text.strip()
                    # Filtrer les marqueurs non-verbaux
                    text = self._filter_non_speech(text)
                    if text:
                        self._inject_text(text)
                        if self.on_text:
                            self.on_text(text)

            except Exception as e:  # pylint: disable=broad-except
                print(f"ERREUR Transcription: {e}")

    def _filter_non_speech(self, text: str) -> str:
        """
        Filtre les marqueurs non-verbaux du texte.

        Args:
            text: Texte brut de Whisper

        Returns:
            str: Texte filtré
        """
        if not text:
            return ""

        # Supprimer les marqueurs connus
        for marker in self.NON_SPEECH_MARKERS:
            text = text.replace(marker, "")

        # Supprimer les marqueurs génériques entre crochets
        import re  # pylint: disable=import-outside-toplevel
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)

        return text.strip()

    def _inject_text(self, text: str):
        """
        Injecte le texte reconnu dans l'application active.

        Args:
            text: Texte à injecter
        """
        injector = self._get_injector()
        if injector:
            # Ajouter un espace après le texte pour séparer des mots suivants
            injector.inject_text(text + " ")
