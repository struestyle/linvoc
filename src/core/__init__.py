"""Core module - Environment detection, dictation, and text injection."""

from .environment import EnvironmentDetector
from .dictation import DictationManager
from .text_injector import TextInjector

__all__ = ["EnvironmentDetector", "DictationManager", "TextInjector"]
