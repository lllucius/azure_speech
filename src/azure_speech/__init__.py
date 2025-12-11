"""
Lightweight Azure Speech REST SDK wrapper.

This SDK mimics the official Azure Speech SDK for Python as closely as possible.
You can use either the official-style API (SpeechSynthesizer, SpeechRecognizer) or
the simplified SpeechClient API.
"""
from .client import (
    AudioConfig,
    AzureSpeechError,
    ResultReason,
    SpeechClient,
    SpeechRecognitionResult,
    SpeechRecognizer,
    SpeechSynthesisResult,
    SpeechSynthesizer,
    SpeechTranslationResult,
)
from .config import SpeechConfig

__all__ = [
    "AudioConfig",
    "AzureSpeechError",
    "ResultReason",
    "SpeechClient",
    "SpeechConfig",
    "SpeechRecognitionResult",
    "SpeechRecognizer",
    "SpeechSynthesisResult",
    "SpeechSynthesizer",
    "SpeechTranslationResult",
]
