"""Tests for the official Azure Speech SDK API compatibility."""
import asyncio

import httpx
import pytest

from azure_speech import (
    AudioConfig,
    AzureSpeechError,
    ResultReason,
    SpeechConfig,
    SpeechRecognizer,
    SpeechSynthesizer,
)


def test_speech_synthesizer_speak_text_async_uses_subscription_key():
    """Test SpeechSynthesizer.speak_text_async with subscription key."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Ocp-Apim-Subscription-Key"] == "test-key"
        assert request.headers["X-Microsoft-OutputFormat"] == "audio-16khz-32kbitrate-mono-mp3"
        assert request.url == httpx.URL("https://eastus.tts.speech.microsoft.com/cognitiveservices/v1")
        return httpx.Response(200, content=b"audio-bytes", headers={"X-RequestId": "req-123"})

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, transport=transport)

    result = synthesizer.speak_text_async("hello world")

    assert result.audio == b"audio-bytes"
    assert result.request_id == "req-123"
    assert result.format == "audio-16khz-32kbitrate-mono-mp3"
    assert result.reason == ResultReason.SynthesizingAudioCompleted


def test_speech_synthesizer_with_audio_config():
    """Test SpeechSynthesizer accepts AudioConfig parameter."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"audio-bytes")

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    audio_config = AudioConfig(filename="output.wav")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config, transport=transport)

    result = synthesizer.speak_text_async("hello")
    assert result.audio == b"audio-bytes"


def test_speech_synthesizer_speak_ssml_async():
    """Test SpeechSynthesizer.speak_ssml_async."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert b"<speak" in request.content
        return httpx.Response(200, content=b"ssml-audio", headers={"X-RequestId": "req-456"})

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, transport=transport)

    ssml = '<speak version="1.0" xml:lang="en-US"><voice name="en-US-JennyNeural">Hello</voice></speak>'
    result = synthesizer.speak_ssml_async(ssml)

    assert result.audio == b"ssml-audio"
    assert result.request_id == "req-456"


def test_speech_recognizer_recognize_once_async_with_bearer_token():
    """Test SpeechRecognizer.recognize_once_async with bearer token."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token-123"
        assert request.url.params.get("language") == "en-US"
        return httpx.Response(
            200,
            json={
                "DisplayText": "hello speech",
                "Duration": 100,
                "Offset": 5,
            },
        )

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(authorization_token="token-123", region="eastus")
    recognizer = SpeechRecognizer(speech_config=speech_config, transport=transport)

    result = recognizer.recognize_once_async(b"\x00\x01", language="en-US")

    assert result.text == "hello speech"
    assert result.duration == 100
    assert result.offset == 5
    assert result.reason == ResultReason.RecognizedSpeech
    assert result.raw["DisplayText"] == "hello speech"


def test_speech_recognizer_with_audio_config():
    """Test SpeechRecognizer accepts AudioConfig parameter."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"DisplayText": "test", "Duration": 50, "Offset": 0})

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    audio_config = AudioConfig(use_default_microphone=True)
    recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, transport=transport)

    result = recognizer.recognize_once_async(b"audio-data")
    assert result.text == "test"


def test_speech_config_constructor():
    """Test SpeechConfig can be constructed with named parameters."""
    # Test with subscription key
    config1 = SpeechConfig(subscription="key123", region="westus")
    assert config1.subscription_key == "key123"
    assert config1.region == "westus"

    # Test with authorization token
    config2 = SpeechConfig(authorization_token="token456", region="eastus")
    assert config2.authorization_token == "token456"
    assert config2.region == "eastus"


def test_result_reason_enum():
    """Test ResultReason enum values."""
    assert ResultReason.RecognizedSpeech.value == 3
    assert ResultReason.SynthesizingAudioCompleted.value == 9
    assert ResultReason.NoMatch.value == 0
    assert ResultReason.Canceled.value == 1


def test_speech_synthesizer_context_manager():
    """Test SpeechSynthesizer works as context manager."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"audio")

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")

    with SpeechSynthesizer(speech_config=speech_config, transport=transport) as synthesizer:
        result = synthesizer.speak_text_async("test")
        assert result.audio == b"audio"


def test_speech_recognizer_context_manager():
    """Test SpeechRecognizer works as context manager."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"DisplayText": "test"})

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")

    with SpeechRecognizer(speech_config=speech_config, transport=transport) as recognizer:
        result = recognizer.recognize_once_async(b"audio")
        assert result.text == "test"


def test_speech_synthesizer_async_real():
    """Test truly async method of SpeechSynthesizer."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"async-audio")

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config, async_transport=transport)

    async def run():
        result = await synthesizer.speak_text_async_real("hello async")
        return result

    result = asyncio.run(run())
    assert result.audio == b"async-audio"


def test_speech_recognizer_async_real():
    """Test truly async method of SpeechRecognizer."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"DisplayText": "async test"})

    transport = httpx.MockTransport(handler)
    speech_config = SpeechConfig(subscription="test-key", region="eastus")
    recognizer = SpeechRecognizer(speech_config=speech_config, async_transport=transport)

    async def run():
        result = await recognizer.recognize_once_async_real(b"audio")
        return result

    result = asyncio.run(run())
    assert result.text == "async test"


def test_audio_config_initialization():
    """Test AudioConfig initialization."""
    # Default initialization
    config1 = AudioConfig()
    assert config1.use_default_microphone is False
    assert config1.filename is None

    # With microphone
    config2 = AudioConfig(use_default_microphone=True)
    assert config2.use_default_microphone is True

    # With filename
    config3 = AudioConfig(filename="audio.wav")
    assert config3.filename == "audio.wav"
