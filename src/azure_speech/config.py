from typing import Optional


class SpeechConfig:
    """Configuration for Azure Speech REST endpoints.
    
    Mimics the official Azure Speech SDK's SpeechConfig class.
    """

    def __init__(
        self,
        *,
        subscription: Optional[str] = None,
        region: str,
        authorization_token: Optional[str] = None,
        endpoint: Optional[str] = None,
        speech_synthesis_voice_name: str = "en-US-JennyNeural",
        speech_recognition_language: str = "en-US",
        # Support both parameter names for backward compatibility
        subscription_key: Optional[str] = None,
    ) -> None:
        """Initialize SpeechConfig.
        
        Args:
            subscription: Azure subscription key (official SDK parameter name)
            region: Azure region (e.g., 'eastus', 'westus')
            authorization_token: Authorization token (alternative to subscription key)
            endpoint: Custom endpoint URL (optional)
            speech_synthesis_voice_name: Default voice for synthesis
            speech_recognition_language: Default language for recognition
            subscription_key: Alias for 'subscription' (backward compatibility)
        """
        self.region = region
        # Support both 'subscription' and 'subscription_key' parameters
        self.subscription_key = subscription or subscription_key
        self.authorization_token = authorization_token
        self.endpoint = endpoint
        self.speech_synthesis_voice_name = speech_synthesis_voice_name
        self.speech_recognition_language = speech_recognition_language

    @classmethod
    def from_subscription(cls, subscription_key: str, region: str, **kwargs) -> "SpeechConfig":
        """Create SpeechConfig from subscription key.
        
        Args:
            subscription_key: Azure subscription key
            region: Azure region
            **kwargs: Additional configuration options
            
        Returns:
            SpeechConfig instance
        """
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
