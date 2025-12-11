"""
Lightweight Azure Speech REST SDK wrapper.
"""
from .client import (
    AzureSpeechError,
    SpeechClient,
    SpeechRecognitionResult,
    SpeechSynthesisResult,
    SpeechTranslationResult,
)
from .config import SpeechConfig

__all__ = [
    "AzureSpeechError",
    "SpeechClient",
    "SpeechConfig",
    "SpeechRecognitionResult",
    "SpeechSynthesisResult",
    "SpeechTranslationResult",
]
