from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeechConfig:
    """Configuration for Azure Speech REST endpoints."""

    region: str
    subscription_key: Optional[str] = None
    authorization_token: Optional[str] = None
    endpoint: Optional[str] = None
    speech_synthesis_voice_name: str = "en-US-JennyNeural"
    speech_recognition_language: str = "en-US"

    @classmethod
    def from_subscription(cls, subscription_key: str, region: str, **kwargs) -> "SpeechConfig":
        return cls(region=region, subscription_key=subscription_key, **kwargs)

    @classmethod
    def from_authorization_token(cls, token: str, region: str, **kwargs) -> "SpeechConfig":
        return cls(region=region, authorization_token=token, **kwargs)

    @property
    def _tts_base(self) -> str:
        if self.endpoint:
            return self.endpoint.rstrip("/")
        return f"https://{self.region}.tts.speech.microsoft.com"

    @property
    def _stt_base(self) -> str:
        if self.endpoint:
            return self.endpoint.rstrip("/")
        return f"https://{self.region}.stt.speech.microsoft.com"

    @property
    def tts_url(self) -> str:
        return f"{self._tts_base}/cognitiveservices/v1"

    @property
    def stt_url(self) -> str:
        return f"{self._stt_base}/speech/recognition/conversation/cognitiveservices/v1"

    @property
    def translation_url(self) -> str:
        return f"{self._stt_base}/speech/translation/cognitiveservices/v1"

    def validate(self) -> None:
        if not self.region:
            raise ValueError("region is required for SpeechConfig")
        if not (self.subscription_key or self.authorization_token):
            raise ValueError("Either subscription_key or authorization_token must be provided.")
