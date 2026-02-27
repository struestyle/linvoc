"""Moteur de reconnaissance basé sur les modèles Parakeet de NVIDIA."""

from __future__ import annotations

import os
import tempfile
import threading
import wave
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, cast

from .engine_base import DictationState, EngineType, SpeechEngine
from .text_injector import TextInjector, TextInjectorBackend

if TYPE_CHECKING:  # pragma: no cover - uniquement pour hints
    from nemo.collections.asr.models import ASRModel


class ParakeetEngine(SpeechEngine):
    """Implémentation basé sur NeMo Parakeet (RNNT / CTC)."""

    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    DEFAULT_MODEL = "nvidia/parakeet-tdt-0.6b-v3"

    SIZE_TO_MODEL = {
        "tiny": "nvidia/parakeet-rnnt-0.6b",
        "base": "nvidia/parakeet-rnnt-1.1b",
        "small": "nvidia/parakeet-tdt-0.6b-v3",
        "medium": "nvidia/parakeet-tdt-0.6b-v3",
        "large": "nvidia/parakeet-tdt-1.1b-v2",
    }

    def __init__(
        self,
        language: str = "fr",
        model_size: str = "base",
        model_name: Optional[str] = None,
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        super().__init__(language, on_text, on_state_change)
        self._model_size = model_size
        self._requested_model = model_name
        self.model_name = model_name or self.SIZE_TO_MODEL.get(model_size, self.DEFAULT_MODEL)
        self._model: Optional["ASRModel"] = None
        self._recording = False
        self._audio_thread: Optional[threading.Thread] = None
        self._frames: list[bytes] = []
        self._injector: Optional[TextInjectorBackend] = None

    @property
    def engine_type(self) -> EngineType:
        return EngineType.PARAKEET

    def is_available(self) -> bool:
        try:
            import nemo.collections.asr.models  # pylint: disable=unused-import
            import torch  # pylint: disable=unused-import
            return True
        except ImportError:
            return False

    def _resolve_device(self) -> Any:
        try:
            import torch

            if torch.cuda.is_available():
                return torch.device("cuda")
            return torch.device("cpu")
        except ImportError:
            pass
        return "cpu"

    def _resolve_model_name(self) -> str:
        if self._requested_model:
            return self._requested_model
        return self.SIZE_TO_MODEL.get(self._model_size, self.DEFAULT_MODEL)

    def _load_model(self) -> bool:
        if self._model is not None:
            return True

        try:
            from nemo.collections.asr.models import ASRModel  # pylint: disable=import-outside-toplevel

            model_name = self._resolve_model_name()
            self.model_name = model_name
            device = self._resolve_device()

            self._model = cast(
                "ASRModel",
                ASRModel.from_pretrained(  # type: ignore[arg-type]
                    model_name,
                    map_location=device,
                ),
            )
            self._configure_language()
            self._model.eval()
            return True
        except Exception as exc:  # pylint: disable=broad-except
            print(f"ERREUR Chargement Parakeet: {exc}")
            self._model = None
            return False

    def _get_injector(self) -> Optional[TextInjectorBackend]:
        if self._injector is None:
            try:
                self._injector = TextInjector.get_instance()
            except RuntimeError:
                self._injector = None
        return self._injector

    def start(self) -> bool:
        if self._recording:
            return False

        if not self.is_available():
            print("ERREUR: nemo_toolkit ou torch non installé")
            self.state = DictationState.ERROR
            return False

        if not self._load_model():
            self.state = DictationState.ERROR
            return False

        self._frames = []
        self._recording = True
        self._audio_thread = threading.Thread(
            target=self._capture_audio,
            daemon=True,
        )
        self._audio_thread.start()

        self.state = DictationState.RECORDING
        return True

    def stop(self) -> str:
        if not self._recording:
            return ""

        self.state = DictationState.PROCESSING
        self._recording = False

        if self._audio_thread and self._audio_thread.is_alive():
            self._audio_thread.join(timeout=30)

        if self._frames:
            self._transcribe_frames(self._frames)
            self._frames = []

        self.state = DictationState.IDLE
        return ""

    def preload(self) -> bool:
        """Charge le modèle à l'avance sans démarrer la capture."""
        if not self.is_available():
            return False
        return self._load_model()

    def _capture_audio(self):
        try:
            import pyaudio  # pylint: disable=import-outside-toplevel
        except ImportError:
            print("ERREUR: PyAudio non installé")
            self.state = DictationState.ERROR
            self._recording = False
            return

        audio = pyaudio.PyAudio()

        try:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE,
            )
        except OSError as exc:
            print(f"ERREUR Microphone: {exc}")
            audio.terminate()
            self.state = DictationState.ERROR
            self._recording = False
            return

        try:
            while self._recording:
                try:
                    data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    self._frames.append(data)
                except OSError:
                    continue
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def _transcribe_frames(self, frames: list[bytes]):
        if not frames or self._model is None:
            return
        model = self._model
        assert model is not None  # pour type checkers

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            with wave.open(temp_file.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.SAMPLE_RATE)
                wav_file.writeframes(b"".join(frames))

            try:
                segments = model.transcribe(  # type: ignore[call-arg]
                    [temp_file.name],
                    batch_size=1,
                )
            except Exception as exc:  # pylint: disable=broad-except
                print(f"ERREUR Transcription Parakeet: {exc}")
                return

        texts = self._extract_texts(segments)
        if not texts:
            return

        final_text = texts[0]

        injector = self._get_injector()
        if injector:
            injector.inject_text(final_text + " ")

        if self.on_text:
            self.on_text(final_text)

    def _configure_language(self):
        """Configure le tokenizer/langue si supporté."""
        model = self._model
        if model is None:
            return
        lang = self.language.lower()

        cfg = getattr(model, "cfg", None)
        if cfg is None:
            return

        if hasattr(cfg, "decoding"):
            try:
                current_lang = getattr(cfg.decoding, "language", None)
                if current_lang and hasattr(model, "change_decoding_language"):
                    getattr(model, "change_decoding_language")(lang)
                setattr(cfg.decoding, "language", lang)
            except Exception:
                pass

    def _extract_texts(self, raw_segments: Optional[Iterable[Any]]) -> list[str]:
        """Normalise la sortie de NeMo (str, Hypothesis, dict)."""
        texts: list[str] = []
        if not raw_segments:
            return texts

        for entry in raw_segments:
            candidate = ""

            if isinstance(entry, str):
                candidate = entry
            elif isinstance(entry, dict):
                candidate = str(entry.get("text", ""))
            elif hasattr(entry, "text"):
                candidate = str(getattr(entry, "text", ""))
            elif isinstance(entry, (list, tuple)):
                for sub in entry:
                    if isinstance(sub, str):
                        candidate = sub
                        break
                    if hasattr(sub, "text"):
                        candidate = str(getattr(sub, "text", ""))
                        break

            candidate = candidate.strip()
            if candidate:
                texts.append(candidate)

        return texts
