import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterable, Dict, Iterable, Optional

import httpx

from .config import SpeechConfig


class AzureSpeechError(Exception):
    """Raised when Azure Speech REST API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


@dataclass
class SpeechSynthesisResult:
    audio: bytes
    request_id: Optional[str]
    format: str


@dataclass
class SpeechRecognitionResult:
    text: str
    duration: Optional[int]
    offset: Optional[int]
    raw: Dict


@dataclass
class SpeechTranslationResult:
    translations: Dict[str, str]
    recognized: Optional[str]
    raw: Dict


def build_ssml(
    text: str,
    *,
    voice: str,
    language: str,
    style: Optional[str] = None,
    rate: Optional[str] = None,
    pitch: Optional[str] = None,
) -> str:
    """Create a minimal SSML document for text-to-speech."""
    prosody_attrs = []
    if rate:
        prosody_attrs.append(f'rate="{rate}"')
    if pitch:
        prosody_attrs.append(f'pitch="{pitch}"')
    prosody_open = f"<prosody {' '.join(prosody_attrs)}>" if prosody_attrs else ""
    prosody_close = "</prosody>" if prosody_attrs else ""
    express = f' style="{style}"' if style else ""
    return (
        '<speak version="1.0" '
        f'xml:lang="{language}">'
        f'<voice xml:lang="{language}" name="{voice}"{express}>'
        f"{prosody_open}{text}{prosody_close}"
        "</voice>"
        "</speak>"
    )


class SpeechClient:
    """Lightweight wrapper around Azure Speech REST APIs."""

    def __init__(
        self,
        config: SpeechConfig,
        *,
        timeout: float = 15.0,
        transport: Optional[httpx.BaseTransport] = None,
        async_transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        config.validate()
        self.config = config
        self._client = httpx.Client(timeout=timeout, transport=transport)
        self._async_client = httpx.AsyncClient(timeout=timeout, transport=async_transport)

    def close(self) -> None:
        self._client.close()
        if self._async_client.is_closed:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._async_client.aclose())
        else:
            # When already inside a running loop, rely on async context managers or explicit aclose().
            pass

    def __enter__(self) -> "SpeechClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    async def __aenter__(self) -> "SpeechClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if not self._async_client.is_closed:
            await self._async_client.aclose()

    def speak_text(
        self,
        text: str,
        *,
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        voice: Optional[str] = None,
        style: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        language: Optional[str] = None,
        ssml: Optional[str] = None,
    ) -> SpeechSynthesisResult:
        """Convert text to audio bytes."""
        payload = ssml or build_ssml(
            text,
            voice=voice or self.config.speech_synthesis_voice_name,
            language=language or self.config.speech_recognition_language,
            style=style,
            rate=rate,
            pitch=pitch,
        )
        headers = self._auth_headers()
        headers.update(
            {
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": output_format,
            }
        )
        response = self._client.post(self.config.tts_url, headers=headers, content=payload.encode("utf-8"))
        self._raise_for_status(response)
        return SpeechSynthesisResult(
            audio=response.content,
            request_id=response.headers.get("X-RequestId"),
            format=output_format,
        )

    async def speak_text_async(
        self,
        text: str,
        *,
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        voice: Optional[str] = None,
        style: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        language: Optional[str] = None,
        ssml: Optional[str] = None,
    ) -> SpeechSynthesisResult:
        """Async: convert text to audio bytes."""
        payload = ssml or build_ssml(
            text,
            voice=voice or self.config.speech_synthesis_voice_name,
            language=language or self.config.speech_recognition_language,
            style=style,
            rate=rate,
            pitch=pitch,
        )
        headers = self._auth_headers()
        headers.update(
            {
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": output_format,
            }
        )
        response = await self._async_client.post(self.config.tts_url, headers=headers, content=payload.encode("utf-8"))
        self._raise_for_status(response)
        return SpeechSynthesisResult(
            audio=response.content,
            request_id=response.headers.get("X-RequestId"),
            format=output_format,
        )

    def stream_synthesis(
        self,
        text: str,
        *,
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        voice: Optional[str] = None,
        style: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        language: Optional[str] = None,
        ssml: Optional[str] = None,
    ) -> Iterable[bytes]:
        """Stream synthesized audio in chunks."""
        payload = ssml or build_ssml(
            text,
            voice=voice or self.config.speech_synthesis_voice_name,
            language=language or self.config.speech_recognition_language,
            style=style,
            rate=rate,
            pitch=pitch,
        )
        headers = self._auth_headers()
        headers.update(
            {
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": output_format,
            }
        )
        with self._client.stream("POST", self.config.tts_url, headers=headers, content=payload.encode("utf-8")) as resp:
            self._raise_for_status(resp)
            for chunk in resp.iter_bytes():
                if chunk:
                    yield chunk

    async def stream_synthesis_async(
        self,
        text: str,
        *,
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        voice: Optional[str] = None,
        style: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        language: Optional[str] = None,
        ssml: Optional[str] = None,
    ) -> AsyncIterable[bytes]:
        """Async generator: stream synthesized audio in chunks."""
        payload = ssml or build_ssml(
            text,
            voice=voice or self.config.speech_synthesis_voice_name,
            language=language or self.config.speech_recognition_language,
            style=style,
            rate=rate,
            pitch=pitch,
        )
        headers = self._auth_headers()
        headers.update(
            {
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": output_format,
            }
        )
        async with self._async_client.stream(
            "POST", self.config.tts_url, headers=headers, content=payload.encode("utf-8")
        ) as resp:
            self._raise_for_status(resp)
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk

    def recognize(
        self,
        audio: bytes,
        *,
        language: Optional[str] = None,
        format: str = "simple",
        content_type: str = "audio/wav",
    ) -> SpeechRecognitionResult:
        """Run speech-to-text on the provided audio bytes."""
        params = {"language": language or self.config.speech_recognition_language, "format": format}
        headers = self._auth_headers()
        headers["Content-Type"] = content_type
        response = self._client.post(self.config.stt_url, params=params, headers=headers, content=audio)
        self._raise_for_status(response)
        data = response.json()
        return SpeechRecognitionResult(
            text=data.get("DisplayText") or data.get("Text") or "",
            duration=data.get("Duration"),
            offset=data.get("Offset"),
            raw=data,
        )

    async def recognize_async(
        self,
        audio: bytes,
        *,
        language: Optional[str] = None,
        format: str = "simple",
        content_type: str = "audio/wav",
    ) -> SpeechRecognitionResult:
        """Async: run speech-to-text on the provided audio bytes."""
        params = {"language": language or self.config.speech_recognition_language, "format": format}
        headers = self._auth_headers()
        headers["Content-Type"] = content_type
        response = await self._async_client.post(self.config.stt_url, params=params, headers=headers, content=audio)
        self._raise_for_status(response)
        data = response.json()
        return SpeechRecognitionResult(
            text=data.get("DisplayText") or data.get("Text") or "",
            duration=data.get("Duration"),
            offset=data.get("Offset"),
            raw=data,
        )

    def translate(
        self,
        audio: bytes,
        *,
        to: Iterable[str],
        from_language: Optional[str] = None,
        content_type: str = "audio/wav",
    ) -> SpeechTranslationResult:
        """Translate spoken audio into the requested languages."""
        targets = list(to)
        if not targets:
            raise ValueError("At least one target language code must be provided.")
        params: Dict[str, Any] = {"from": from_language or self.config.speech_recognition_language, "to": targets}
        headers = self._auth_headers()
        headers["Content-Type"] = content_type
        response = self._client.post(self.config.translation_url, params=params, headers=headers, content=audio)
        self._raise_for_status(response)
        data = response.json()
        translations: Dict[str, str] = {}
        for item in data.get("translations", []):
            if not isinstance(item, dict):
                continue
            language_code = item.get("to")
            if language_code:
                translations[language_code] = item.get("text", "")
        recognized = data.get("text") or data.get("DisplayText")
        return SpeechTranslationResult(translations=translations, recognized=recognized, raw=data)

    async def translate_async(
        self,
        audio: bytes,
        *,
        to: Iterable[str],
        from_language: Optional[str] = None,
        content_type: str = "audio/wav",
    ) -> SpeechTranslationResult:
        """Async: translate spoken audio into the requested languages."""
        targets = list(to)
        if not targets:
            raise ValueError("At least one target language code must be provided.")
        params: Dict[str, Any] = {"from": from_language or self.config.speech_recognition_language, "to": targets}
        headers = self._auth_headers()
        headers["Content-Type"] = content_type
        response = await self._async_client.post(self.config.translation_url, params=params, headers=headers, content=audio)
        self._raise_for_status(response)
        data = response.json()
        translations: Dict[str, str] = {}
        for item in data.get("translations", []):
            if not isinstance(item, dict):
                continue
            language_code = item.get("to")
            if language_code:
                translations[language_code] = item.get("text", "")
        recognized = data.get("text") or data.get("DisplayText")
        return SpeechTranslationResult(translations=translations, recognized=recognized, raw=data)

    def set_authorization_token(self, token: str) -> None:
        """Update bearer token at runtime (useful for short-lived tokens)."""
        self.config.authorization_token = token

    def _auth_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.config.authorization_token:
            headers["Authorization"] = f"Bearer {self.config.authorization_token}"
        elif self.config.subscription_key:
            headers["Ocp-Apim-Subscription-Key"] = self.config.subscription_key
        return headers

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        message = response.text
        details: Dict = {}
        try:
            payload = response.json()
            details = payload
            message = (
                payload.get("error", {}).get("message")
                or payload.get("message")
                or payload.get("statusText")
                or message
            )
        except ValueError:
            pass
        raise AzureSpeechError(message=message, status_code=response.status_code, details=details)
