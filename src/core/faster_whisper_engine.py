"""Moteur de reconnaissance basé sur FasterWhisper."""

from __future__ import annotations

import os
import tempfile
import threading
import wave
from typing import Callable, Optional

from .engine_base import DictationState, EngineType, SpeechEngine
from .text_injector import TextInjectorBackend


class FasterWhisperEngine(SpeechEngine):
    """Implémentation basée sur FasterWhisper pour transcription rapide."""

    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024

    def __init__(
        self,
        language: str = "fr",
        model_size: str = "base",
        on_text: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[DictationState], None]] = None,
    ):
        super().__init__(language, on_text, on_state_change)
        self._model_size = model_size
        self._model = None
        self._recording = False
        self._audio_thread: Optional[threading.Thread] = None
        self._frames: list[bytes] = []
        self._injector: Optional[TextInjectorBackend] = None

    @property
    def engine_type(self) -> EngineType:
        return EngineType.WHISPER  # Même type, variante

    def is_available(self) -> bool:
        try:
            from faster_whisper import WhisperModel  # pylint: disable=unused-import
            return True
        except ImportError:
            return False

    def _load_model(self) -> bool:
        if self._model is not None:
            return True

        try:
            from faster_whisper import WhisperModel  # pylint: disable=import-outside-toplevel

            device = "cuda" if self._is_cuda_available() else "cpu"
            self._model = WhisperModel(self._model_size, device=device, compute_type="int8")
            return True
        except Exception as exc:  # pylint: disable=broad-except
            print(f"ERREUR Chargement FasterWhisper: {exc}")
            return False

    def _is_cuda_available(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
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
            print("ERREUR: faster-whisper non installé")
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

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            with wave.open(temp_file.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.SAMPLE_RATE)
                wav_file.writeframes(b"".join(frames))

            try:
                segments, _ = self._model.transcribe(
                    temp_file.name,
                    language=self.language,
                    beam_size=5,
                )
                text = " ".join(segment.text for segment in segments).strip()
                if text:
                    injector = self._get_injector()
                    if injector:
                        injector.inject_text(text + " ")
                    if self.on_text:
                        self.on_text(text)
            except Exception as exc:  # pylint: disable=broad-except
                print(f"ERREUR Transcription FasterWhisper: {exc}")